# Python imports
import os
from os.path import join

# project imports
from .common import *

# uncomment the following line to include i18n
# from .i18n import *

# ##### DEBUG CONFIGURATION ###############################
DEBUG = True

# allow all hosts during development
ALLOWED_HOSTS = ['*']

# ##### APPLICATION CONFIGURATION #########################

INSTALLED_APPS = DEFAULT_APPS

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
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'guidetoexile': {
            'handlers': ['console', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

ASSET_DIR = r'poe_assets'
BASE_ITEMS_LOOKUP_FILE = r'poe_assets\base_items_lookup.json'
UNIQUE_ITEMS_LOOKUP_FILE = r'poe_assets\unique_items_lookup.json'
GEMS_FILE = r'poe_assets\gems.min.json'
