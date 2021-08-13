# Python imports
import sys
from os.path import abspath, basename, dirname, join, normpath

# ##### PATH CONFIGURATION ################################

# fetch Django's project directory
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# fetch the project_root
PROJECT_ROOT = dirname(DJANGO_ROOT)

# the name of the whole site
SITE_NAME = basename(DJANGO_ROOT)

# collect static files here
STATIC_ROOT = join(PROJECT_ROOT, 'run', 'static')

# collect media files here
MEDIA_ROOT = join(PROJECT_ROOT, 'run', 'media')

# look for static assets here
STATICFILES_DIRS = [
    join(PROJECT_ROOT, 'static'),
]

# look for templates here
# This is an internal setting, used in the TEMPLATES directive
PROJECT_TEMPLATES = [
    join(PROJECT_ROOT, 'templates'),
    join(PROJECT_ROOT, 'app/django_tiptap/templates')
]

# add apps/ to the Python path
sys.path.append(normpath(join(PROJECT_ROOT, 'apps')))

# ##### APPLICATION CONFIGURATION #########################

# these are the apps
DEFAULT_APPS = [
    'GuideToExile',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'apps.django_tiptap',
]

# Middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# template stuff
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': PROJECT_TEMPLATES,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages'
            ],
        },
    },
]

# Internationalization
USE_I18N = False

# ##### SECURITY CONFIGURATION ############################

# We store the secret key here
# The required SECRET_KEY is fetched at the end of this file
SECRET_FILE = normpath(join(PROJECT_ROOT, 'run', 'SECRET.key'))

# these persons receive error notification
ADMINS = (
    ('your name', 'your_name@example.com'),
)
MANAGERS = ADMINS

# ##### DJANGO RUNNING CONFIGURATION ######################

# the default WSGI application
WSGI_APPLICATION = '%s.wsgi.application' % SITE_NAME

# the root URL configuration
ROOT_URLCONF = '%s.urls' % SITE_NAME

# the URL for static files
STATIC_URL = '/static/'

# the URL for media files
MEDIA_URL = '/media/'

LOGIN_REDIRECT_URL = '/'

# ##### DEBUG CONFIGURATION ###############################
DEBUG = False

DJANGO_TIPTAP_CONFIG = {
    "width": "500px",
    "height": "500px",
    "extensions": [
        # to see what each extension does, refer to [tiptap.dev](https://www.tiptap.dev/)
        "bold",
        "italic",
        "underline",
        "strikethrough",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "textAlign",
        "indent",
        "bulletList",
        "orderedList",
        "typography",
        "clearFormat"
    ],
    "placeholderText": "Begin typing here...",  # set None to skip display
    "unsavedChangesWarningText": "You have unsaved changes",  # set None to skip display
    "lang": "EN",  # if you want to use default tooltips and translations, use this. Valid Options => EN/DE(for now)
    "tooltips": {
        # if you want to use your custom tooltips(maybe because you don't prefer default or the language you want isn't there)
        "bold": "Bold | (ctrl / ⌘) + B",
        "italic": "Italic | (ctrl / ⌘) + I",
        "underline": "Underline | (ctrl / ⌘) + U",
        "strike": "Strikethrough | (ctrl / ⌘) + shift + X",
        "h1": "Header 1 | (ctrl + alt) / (⌘ + ⌥) + 1",
        "h2": "Header 2 | (ctrl + alt) / (⌘ + ⌥) + 2",
        "h3": "Header 3 | (ctrl + alt) / (⌘ + ⌥) + 3",
        "h4": "Header 4 | (ctrl + alt) / (⌘ + ⌥) + 4",
        "h5": "Header 5 | (ctrl + alt) / (⌘ + ⌥) + 5",
        "h6": "Header 6 | (ctrl + alt) / (⌘ + ⌥) + 6",
        "alignLeft": "Align Left | (ctrl + shift ⇧) / (⌘ + shift ⇧) + L",
        "alignCenter": "Align Center | (ctrl + shift ⇧) / (⌘ + shift ⇧) + E",
        "alignRight": "Align Right | (ctrl + shift ⇧) / (⌘ + shift ⇧) + R",
        "alignJustify": "Justify | (ctrl + shift ⇧) / (⌘ + shift ⇧) + J",
        "indent": "Indent (Tab ↹)",
        "outdent": "Outdent (shift ⇧ + Tab ↹)",
        "bulletList": "Bullet List | (ctrl + shift ⇧) / (⌘ + shift ⇧) + 8",
        "orderedList": "Numbered List | (ctrl + shift ⇧) / (⌘ + shift ⇧) + 7",
        "addTable": "Add Table",
        "deleteTable": "Delete Table",
        "addColumnBefore": "Add Column Before",
        "addColumnAfter": "Add Column After",
        "deleteColumn": "Delete Column",
        "addRowBefore": "Add Row Before",
        "addRowAfter": "Add Row After",
        "deleteRow": "Delete Row",
        "mergeCells": "Merge Cells",
        "splitCell": "Split Cell",
        "toggleHeaderColumn": "Toggle Header Column",
        "toggleHeaderRow": "Toggle Header Row",
        "toggleHeaderCell": "Toggle Header Cell",
        "clearFormat": "Clear Format",
        "jinjaHighlight": "",
    },
    "translations": {
        # if the lang you defined exists in the default langs, then no need to define translations
        "row": "Row",
        "column": "Column",
        "add": "Add"
    },
    "custom_extensions": [
        {
            "source_static": "tiptap_extension/span_extension.js",
            "module_name": "SpanExtension",
        }
    ]

}
ASC_TREE_X = 7000
ASC_TREE_Y = -5500

# finally grab the SECRET KEY
try:
    SECRET_KEY = open(SECRET_FILE).read().strip()
except IOError:
    try:
        from django.utils.crypto import get_random_string

        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!$%&()=+-_'
        SECRET_KEY = get_random_string(50, chars)
        with open(SECRET_FILE, 'w') as f:
            f.write(SECRET_KEY)
    except IOError:
        raise Exception('Could not open %s for writing!' % SECRET_FILE)
