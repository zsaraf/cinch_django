import os
import hashlib
from rest_framework import authentication
from rest_framework import exceptions
from sesh.exceptions import BadLogin, AccountDisabled, PendingTutorReady, PendingTutorNotReady
from django.db.models import Q
from django.contrib.auth.models import AnonymousUser
from .models import User, Token, Device
from apps.tutor.models import PendingTutor
import json
import logging
logger = logging.getLogger(__name__)


class SeshAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_X_SESSION_ID')
        if not token:
            if os.path.basename(os.path.normpath(request.path)) == "login":
                return self.authenticate_login(request)
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

        request_data = json.loads(request.body)

        email = request_data.get('email')
        password = request_data.get("password")
        device_type = request_data.get("type")
        device_model = request_data.get("device_model")
        system_version = request_data.get("system_version")
        app_version = request_data.get("app_version")
        timezone_name = request_data.get("timezone_name")
        is_web = request_data.get("is_web")

        # see if a user exists with the email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:

            # see if a pending tutor exists with the email
            try:
                pt = PendingTutor.objects.get(email=email)
                if pt.ready_to_publish:
                    raise PendingTutorReady()
                else:
                    raise PendingTutorNotReady()
            except PendingTutor.DoesNotExist:
                pass
            raise BadLogin()

        str_to_hash = 'Eabltf1!' + user.salt + password
        m = hashlib.sha1()
        m.update(str_to_hash)
        hex_dig = m.hexdigest()

        if user.password == hex_dig:

            # If user isn't enabled -- don't let them in
            if user.is_disabled:
                raise AccountDisabled()

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
            raise BadLogin()
