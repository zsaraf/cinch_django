from apps.account.models import User, Token
from rest_framework import authentication
from rest_framework import exceptions
from django.db.models import Q

import logging
logger = logging.getLogger(__name__)


class SeshAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_X_SESSION_ID')
        if not token:
            return None

        try:
            tokenId = Token.objects.get(session_id=token).id
            logger.debug(tokenId)
            user = User.objects.get(Q(token_id=tokenId) | Q(web_token_id=tokenId))
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such token')

        return (user, token)
