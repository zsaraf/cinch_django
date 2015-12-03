from rest_framework.exceptions import APIException


class BadLogin(APIException):
    status_code = 401
    default_detail = 'Invalid email/password combination.'


class AccountDisabled(APIException):
    status_code = 401
    default_detail = 'Your account has been disabled. Please contact team@seshtutoring.com for more information.'


class PendingTutorReady(APIException):
    status_code = 401
    default_detail = 'Thanks for signing up to tutor! You still need to create an account. Please use the same email address and you will be enabled to tutor.'


class PendingTutorNotReady(APIException):
    status_code = 401
    default_detail = 'Thanks for signing up to tutor! We\'ve received your tutor application and will get back to you once you\'ve been approved. In the mean time, please create an account with the same email address.'
