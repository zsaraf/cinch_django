"""
Django settings for sesh project.

Generated by 'django-admin startproject' using Django 1.8.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SERVER_NAME = 'seshtutoring'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

#Slack Integration - for API tips see https://github.com/os/slacker

# Below is the dev (Cinch) slack bot
SLACK_BOT_TOKEN = 'xoxb-18843217328-ICDugF9g9eMKgaxGXkX646yY'

# Below is the prod (Sesh) slack bot
# SLACK_BOT_TOKEN = 'xoxb-18843597536-6nv8LjUVidq2oTtkT0qAQ5OY'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'l%rjm^+u1m_k59lmah+052v!)*4&^mxn7&+y$f6q)tfikpb#$e'

# STRIPE KEY
STRIPE_API_KEY = 'sk_live_71u3DPdgpHfGhNHiYzEVb2jC'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['cinchtutoring.com', 'localhost', 'seshtutoring.com']

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'apps.university',
    'apps.account',
    'apps.student',
    'apps.tutor',
    'apps.chatroom',
    'apps.group',
    'apps.emailclient',
    'apps.tutoring',
    'apps.notification',
    'apps.transaction',
    'storages'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'sesh.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'sesh_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/sesh.log',
            'formatter': 'verbose'
        },
        'django_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose'
        },

    },
    'loggers': {
        'django': {
            'handlers': ['django_file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'apps': {
            'handlers': ['sesh_file'],
            'level': 'DEBUG',
        },
    }
}

WSGI_APPLICATION = 'sesh.wsgi.application'

# REST FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.account.AuthenticationBackend.SeshAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication'
    ),
    'PAGE_SIZE': 10
}

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': '%s/sesh_db.cnf' % ROOT_DIR,
            'charset': 'utf8mb4'
        },
    }
}


AWS_ACCESS_KEY_ID = 'AKIAIIP5DJ2KQYHRULPA'  # Root access key
AWS_SECRET_ACCESS_KEY = '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'  # Root secret access key
AWS_STORAGE_BUCKET_NAME = 'sesh-tutoring-dev'
S3_URL = 'https://%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, "static/")
