# no_debug_settings.py

# pull in the normal settings
from settings import *

# no debug for us
DEBUG = False
SERVER_NAME = 'cinchtutoring'
STRIPE_API_KEY = 'sk_test_qJfmv5RuoEQK9BMDHNBf4I82'
AWS_STORAGE_BUCKET_NAME = 'sesh-tutoring-dev'
S3_URL = 'https://%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
