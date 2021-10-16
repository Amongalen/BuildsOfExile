# for now fetch the development settings only

# project imports

from .common import *

# turn off all debugging

DEBUG = True
LOAD_ALL_SKILLTREES = True

# You will have to determine, which hostnames should be served by Django
ALLOWED_HOSTS = ['172.31.24.7', '35.156.187.198', '35.156.187.198',
                 'guidetoexile-prod-2.eu-central-1.elasticbeanstalk.com',
                 'guidetoexile.com']

# ##### SECURITY CONFIGURATION ############################

# redirects all requests to https
SECURE_SSL_REDIRECT = False
# session cookies will only be set, if https is used
SESSION_COOKIE_SECURE = True
# how long is a session cookie valid?
SESSION_COOKIE_AGE = 1209600

CSRF_COOKIE_SECURE = True

# SECURE_HSTS_SECONDS = 3600
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# validates passwords (very low security, but hey...)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'user_attributes': ('username',)
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# the email address, these error notifications to admins come from
SERVER_EMAIL = 'admin@guidetoexile.com'

# The number of seconds a password reset link is valid for.
PASSWORD_RESET_TIMEOUT = 60 * 60  # 1 hour

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'guidetoexile': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
        }
    }
}

# limits tree loading in debug mode
CURRENT_TREE_VERSION = '3_15'

POB_PATH = join(PROJECT_ROOT, 'pathofbuilding')

if 'RDS_DB_NAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }

AWS_CONFIG_FILE = normpath(join(PROJECT_ROOT, 'run', 'aws.config'))
with open(AWS_CONFIG_FILE) as conf_file:
    conf = json.load(conf_file)
    AWS_STORAGE_BUCKET_NAME = conf['AWS_STORAGE_BUCKET_NAME']
    AWS_S3_REGION_NAME = conf['AWS_S3_REGION_NAME']
    AWS_ACCESS_KEY_ID = conf['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = conf['AWS_SECRET_ACCESS_KEY']
    GUIDE_IMPORT_USERNAME = conf['IMPORTER_USERNAME']
    GUIDE_IMPORT_PASSWORD = conf['IMPORTER_PASSWORD']
    GUIDE_IMPORT_MAIL = conf['IMPORTER_EMAIL']
    EMAIL_HOST_USER = conf['SMTP_USERNAME']
    EMAIL_HOST_PASSWORD = conf['SMTP_PASSWORD']

# Tell django-storages the domain to use to refer to static files.
AWS_S3_CUSTOM_DOMAIN = 'dm58uz647xk6s.cloudfront.net'

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.eu-central-1.amazonaws.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'accounts@guidetoexile.com'
