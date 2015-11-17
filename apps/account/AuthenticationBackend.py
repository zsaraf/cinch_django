from apps.account.models import User, Token
from rest_framework import authentication
from rest_framework import exceptions
import logging
logger = logging.getLogger(__name__)

class SeshAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_X_SESSION_ID')
        logger.debug(token)
        if not token:
            return None

        try:
            user = User.objects.get(token_id=Token.objects.get(session_id=token).id)
            logger.debug(user.school_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')
        except Token.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such token')
            
        return (user, token)