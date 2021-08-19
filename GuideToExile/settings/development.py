# Python imports
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
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

ASSET_DIR = r'poe_assets'
BASE_ITEMS_LOOKUP_FILE = r'poe_assets\base_items_lookup.json'
UNIQUE_ITEMS_LOOKUP_FILE = r'poe_assets\unique_items_lookup.json'
