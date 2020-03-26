import os
from dotenv import load_dotenv
from django.utils.translation import ugettext_lazy as _

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIP_DIR = os.path.dirname("/tmp")
DOTENV_DIR = os.path.join(BASE_DIR, '.env')
ROOT_URLCONF = 'ecommerce.urls'

# Hosts
ALLOWED_HOSTS = []

# Enviroment
load_dotenv(DOTENV_DIR)
ENVIRONMENT = os.environ.get('ENVIRONMENT')
SECRET_KEY = os.environ.get('SECRET_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
DEBUG = True

if ENVIRONMENT == 'production':
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'crispy_forms',

    'core',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Template engine
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

# Athentication
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Account
LOGIN_REDIRECT_URL = '/products'
ACCOUNT_LOGOUT_REDIRECT_URL = '/products'

# Email
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_REQUIRED = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Internationalization
LANGUAGES = (
    ('en', _('English')),
    ('ru', _('Russian')),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static and Media files
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "media/zip")
]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, 'db.sqlite3')
    }
}

# Crispy Forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Site
SITE_ID = 1
