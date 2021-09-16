# for now fetch the development settings only

# project imports
from .common import *

# turn off all debugging

DEBUG = False

# You will have to determine, which hostnames should be served by Django
ALLOWED_HOSTS = []

# ##### SECURITY CONFIGURATION ############################

# redirects all requests to https
SECURE_SSL_REDIRECT = False
# session cookies will only be set, if https is used
# SESSION_COOKIE_SECURE = True
# how long is a session cookie valid?
# SESSION_COOKIE_AGE = 1209600

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
SERVER_EMAIL = 'root@localhost'

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

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # todo change email backend
