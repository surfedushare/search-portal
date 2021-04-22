"""
Django settings for harvester project.

Generated by 'django-admin startproject' using Django 2.2.10.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import sys
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.logging import ignore_logger

from celery.schedules import crontab

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# We're adding the environments directory outside of the project directory to the path
# That way we can load the environments and re-use them in different contexts
# Like maintenance tasks and harvesting tasks
sys.path.append(os.path.join(BASE_DIR, "..", "environments"))
from surfpol import create_configuration_and_session, get_package_info, MODE
from surfpol.logging import POLElasticsearchHandler, create_elasticsearch_handler
# Then we read some variables from the (build) environment
PACKAGE_INFO = get_package_info()
GIT_COMMIT = PACKAGE_INFO.get("commit", "unknown-git-commit")
VERSION = PACKAGE_INFO.get("versions").get("harvester", "0.0.0")
environment, session = create_configuration_and_session(project='harvester')
credentials = session.get_credentials()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = environment.secrets.django.secret_key

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = MODE == "localhost"

# We're disabling the ALLOWED_HOSTS check, because containers will run in a VPC environment
# This environment is expected to be unreachable with disallowed hosts.
# It hurts to have this setting enabled on AWS, because health checks don't pass the domain check.
ALLOWED_HOSTS = ["*"]

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Application definition

INSTALLED_APPS = [
    'harvester',  # first to override runserver command
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_results',
    'datagrowth',

    'core',
    'edurep',
    'sharekit',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'harvester.urls'

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

WSGI_APPLICATION = 'harvester.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'harvester',
        'USER': environment.postgres.user,
        'PASSWORD': environment.secrets.postgres.password,
        'HOST': environment.postgres.host,
        'PORT': environment.postgres.port,
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '..', 'static')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_ALLOW_ALL_ORIGINS = True

if environment.aws.harvest_content_bucket:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_ROOT = ''
    MEDIA_URL = f'https://{environment.aws.harvest_content_bucket}.s3.eu-central-1.amazonaws.com/'
    AWS_STORAGE_BUCKET_NAME = environment.aws.harvest_content_bucket
    AWS_S3_REGION_NAME = 'eu-central-1'
    AWS_DEFAULT_ACL = None
else:
    DEFAULT_FILE_STORAGE = 'core.files.storage.OverwriteStorage'
    MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'media', 'harvester')
    MEDIA_URL = 'http://localhost:8000/media/harvester/'
    AWS_STORAGE_BUCKET_NAME = None

# Rest framework
# https://www.django-rest-framework.org/

REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
}


# Elastic Search
# https://www.elastic.co/guide/index.html

ELASTICSEARCH_IS_AWS = environment.elastic_search.is_aws  # AWS requires signing requests
ELASTICSEARCH_HOST = environment.elastic_search.host
ELASTICSEARCH_PROTOCOL = environment.elastic_search.protocol
ELASTICSEARCH_VERIFY_CERTS = environment.elastic_search.verify_certs  # ignored when protocol != https
ELASTICSEARCH_ANALYSERS = {
    'en': 'english',
    'nl': 'dutch'
}
ELASTICSEARCH_ENABLE_DECOMPOUND_ANALYZERS = environment.elastic_search.enable_decompound_analyzers
ELASTICSEARCH_DECOMPOUND_WORD_LISTS = environment.elastic_search.decompound_word_lists


# Logging
# https://docs.djangoproject.com/en/2.2/topics/logging/
# https://docs.sentry.io/

_logging_enabled = sys.argv[1:2] != ['test']
_log_level = environment.django.logging.level if _logging_enabled else 'CRITICAL'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'django_log_formatter_json.JSONFormatter',
        },
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        }
    },
    'handlers': {
        'json': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'json'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'es_harvest': create_elasticsearch_handler(
            'harvest-logs',
            POLElasticsearchHandler.IndexNameFrequency.WEEKLY,
            environment,
            session
        ),
        'es_documents': create_elasticsearch_handler(
            'document-logs',
            POLElasticsearchHandler.IndexNameFrequency.YEARLY,
            environment,
            session
        ),
    },
    'loggers': {
        'harvester': {
            'handlers': ['es_harvest'] if environment.django.logging.is_elastic else ['console'],
            'level': _log_level,
            'propagate': True,
        },
        'documents': {
            'handlers': ['es_documents'] if environment.django.logging.is_elastic else ['console'],
            'level': _log_level,
            'propagate': True,
        },
    },
}

if not DEBUG:

    def strip_sensitive_data(event, hint):
        user_agent = event.get('request', {}).get('headers', {}).get('User-Agent', None)

        if user_agent:
            del event['request']['headers']['User-Agent']

        return event

    sentry_sdk.init(
        before_send=strip_sensitive_data,
        dsn="https://365ba37a8b544e3199ab60d53920613f@o356528.ingest.sentry.io/5318021",
        environment=environment.env,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        send_default_pii=False  # GDPR requirement
    )
    # We kill all DisallowedHost logging on the servers,
    # because it happens so frequently that we can't do much about it
    ignore_logger('django.security.DisallowedHost')


# Project Open Leermaterialen

MIME_TYPE_TO_FILE_TYPE = {  # TODO: this is Edurep based, how do we want this for other repositories?
    'unknown': 'unknown',
    'application/pdf': 'pdf',
    'application/x-pdf': 'pdf',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'presentation',
    'application/vnd.openxmlformats-officedocument.presentationml.slideshow': 'presentation',
    'application/vnd.ms-powerpoint': 'presentation',
    'application/ppt': 'presentation',
    'application/msword': 'text',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'text',
    'application/rtf': 'text',
    'text/plain': 'text',
    'text/html': 'text',
    'application/vnd.ms-word': 'text',
    'application/vnd.ms-word.document.macroEnabled.12': 'text',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.template': 'text',
    'text/rtf': 'text',
    'application/xhtml+xml': 'text',
    'application/postscript': 'text',
    'application/vnd.ms-publisher': 'text',
    'text/xml': 'text',
    'application/vnd.oasis.opendocument.spreadsheet': 'spreadsheet',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'spreadsheet',
    'application/vnd.ms-excel': 'spreadsheet',
    'video/flv': 'video',
    'video/x-flv': 'video',
    'video/quicktime': 'video',
    'video': 'video',
    'video/x-msvideo': 'video',
    'video/mpeg': 'video',
    'application/x-mplayer2': 'video',
    'video/mp4': 'video',
    'video/x-ms-wmv': 'video',
    'video/x-ms-asf': 'video',
    'image': 'image',
    'image/bmp': 'image',
    'image/pjpeg': 'image',
    'image/png': 'image',
    'image/x-icon': 'image',
    'image/x-ms-bmp': 'image',
    'image/tiff': 'image',
    'image/jpg': 'image',
    'image/gif': 'image',
    'image/jpeg': 'image',
    'application/zip': 'archive',
    'application/x-tar': 'archive',
    'application/x-stuffit': 'archive',
    'application/x-rar-compressed': 'archive',
    'application/x-Wikiwijs-Arrangement': 'archive',
    'audio/mpeg': 'audio',
    'application/x-koan': 'audio',
    'application/vnd.koan': 'audio',
    'audio/midi': 'audio',
    'audio/x-wav': 'audio',
    'application/octet-stream': 'other',
    'application/x-yossymemo': 'digiboard',
    'application/Inspire': 'digiboard',
    'application/x-AS3PE': 'digiboard',
    'application/x-Inspire': 'digiboard',
    'application/x-smarttech-notebook': 'digiboard',
    'application/x-zip-compressed': 'digiboard',
    'application/x-ACTIVprimary3': 'digiboard',
    'application/x-ibooks+zip': 'ebook',
    'message/rfc822': 'message',
    'application/vnd.google-earth.kmz': 'googleearth',
    'application/x-java': 'app',
}


# Celery
# https://docs.celeryproject.org/en/v4.1.0/

CELERY_BROKER_URL = f'redis://{environment.django.redis_host}/0'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_BEAT_SCHEDULE = {
    'harvest': {
        'task': 'harvest',
        'schedule': crontab(
            hour=environment.schedule.harvest.hour,
            minute=environment.schedule.harvest.minute,
        ),
        'args': (environment.schedule.harvest.source,)
    },
    'clean_data': {
        'task': 'clean_data',
        'schedule': crontab(
            hour=0,
            minute=0
        ),
    },
    'sync_sharekit_metadata': {
        'task': 'sync_sharekit_metadata',
        'schedule': crontab(minute="*/5"),
    },
}
CELERY_WORKER_HIJACK_ROOT_LOGGER = False


# Datagrowth
# https://data-scope.com/datagrowth/index.html

DATAGROWTH_DATA_DIR = os.path.join(BASE_DIR, "..", "data", "harvester")
DATAGROWTH_BIN_DIR = os.path.join(BASE_DIR, "harvester", "bin")
DATA_RETENTION_PURGE_AFTER = environment.django.data_retention.purge_after or {}
DATA_RETENTION_KEEP_VERSIONS = environment.django.data_retention.keep_versions


# Sharekit

SHAREKIT_API_KEY = environment.secrets.sharekit.api_key
