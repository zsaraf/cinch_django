import os
import hashlib
from rest_framework import authentication
from rest_framework import exceptions
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth.models import AnonymousUser
from .models import User, Token, Device
from apps.tutor.models import PendingTutor
import logging
logger = logging.getLogger(__name__)


class SeshAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_X_SESSION_ID')
        if not token:
            if os.path.basename(os.path.normpath(request.path)) == "login":
                return (AnonymousUser(), None)
            else:
                return None

        try:
            tokenId = Token.objects.get(session_id=token).id
            user = User.objects.get(Q(token_id=tokenId) | Q(web_token_id=tokenId))
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        return (user, token)

    def authenticate_login(self, request):
        email = request.get('email')
        password = request.get("password")
        device_type = request.get("type")
        device_model = request.get("device_model")
        system_version = request.get("system_version")
        app_version = request.get("app_version")
        timezone_name = request.get("timezone_name")
        is_web = request.get("is_web")

        # see if a user exists with the email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:

            # see if a pending tutor exists with the email
            try:
                pt = PendingTutor.objects.get(email=email)
                first_string = 'Thanks for signing up to tutor!'
                if pt.ready_to_publish:
                    raise exceptions.AuthenticationFailed(first_string + ' You still need to create an account. Please use the same email address and you will be enabled to tutor.')
                else:
                    raise exceptions.AuthenticationFailed(first_string + ' We\'ve received your tutor application and will get back to you once you\'ve been approved. In the mean time, please create an account with the same email address.')
            except PendingTutor.DoesNotExist:
                pass
            raise exceptions.AuthenticationFailed('Invalid email/password combination.')

        str_to_hash = 'Eabltf1!' + user.salt + password
        m = hashlib.sha1()
        m.update(str_to_hash)
        hex_dig = m.hexdigest()

        if user.password == hex_dig:

            # If user isn't enabled -- don't let them in
            if user.is_disabled:
                raise exceptions.AuthenticationFailed('Your account has been disabled. Please contact team@seshtutoring.com for more information.')

            # If isn't verified -- return 200 response with unverified status
            if not user.is_verified:
                return (AnonymousUser(), None)

            # Clear the old tokens and add new ones
            # & Generate a new token for the user
            # Also do web/device specific stuff
            token = Token.objects.generate_new_token()

            if is_web:
                if user.web_token_id:
                    Token.objects.filter(id=user.web_token_id).delete()
                user.web_token_id = token.id
            else:
                if user.token:
                    user.token.delete()
                user.token = token
                Device.objects.update_device_token(user, None, device_type, device_model, system_version, app_version, timezone_name)

            user.save()
            return (user, token)

        else:
            raise exceptions.AuthenticationFailed('Invalid email/password combination.')
