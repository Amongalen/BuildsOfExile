# Python imports
import os
from os.path import join

# project imports
from .common import *

# uncomment the following line to include i18n
# from .i18n import *

# ##### DEBUG CONFIGURATION ###############################
DEBUG = True

# limits tree loading in debug mode
CURRENT_TREE_VERSION = '3_15'

# allow all hosts during development
ALLOWED_HOSTS = ['*']

# ##### APPLICATION CONFIGURATION #########################

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

POB_PATH = r'D:\PathOfBuildingForWebapp'

# This logs any emails sent to the console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} [m={module}] [p={process:d}] [t={thread:d}] {message}',
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
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO'
        },
        # 'django.request': {
        #     'handlers': ['mail_admins'],
        #     'level': 'ERROR',
        #     'propagate': False,
        # },
        'guidetoexile': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}
