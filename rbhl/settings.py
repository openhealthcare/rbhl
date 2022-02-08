# Django settings for rbhl project.
import os
import sys
import urllib

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Support', 'support@openhealthcare.org.uk',),
)

MANAGERS = ADMINS
SERVER_EMAIL = 'support@openhealthcare.org.uk'

try:
    import dj_database_url

    DATABASES = {
        'default': dj_database_url.config(
            default='sqlite:///' + PROJECT_PATH + '/opal.sqlite'
        )
    }
except ImportError:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(PROJECT_PATH, 'opal.sqlite'),
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': ''
        }
    }

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.herokuapp.com',
    '192.168.1.10',
    '10.0.0.112',
]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(PROJECT_PATH, 'assets')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/assets/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '(o6_+tl&ba!!y99*fr4wz8m9ifm)&h2e+q5z-s^t6^oue2&aq3'

if DEBUG:
    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )
else:
    TEMPLATE_LOADERS = (
        ('django.template.loaders.cached.Loader', (
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        )),
    )

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'opal.middleware.AngularCSRFRename',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    # for two factor authentication
    'django_otp.middleware.OTPMiddleware',
    'two_factor.middleware.threadlocals.ThreadLocals',
    'rbhl.middleware.TwoStageAuthenticationRequired',
    'django.contrib.messages.middleware.MessageMiddleware',
    'opal.middleware.DjangoReversionWorkaround',
    'reversion.middleware.RevisionMiddleware',
    'rbhl.middleware.SecurityHeadersMiddleware',
)

ROOT_URLCONF = 'rbhl.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'rbhl.wsgi.application'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_PATH, 'templates'),
        ],
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
                'django.contrib.messages.context_processors.messages',
                'opal.context_processors.settings',
                'opal.context_processors.models',
                'opal.core.pathway.context_processors.pathways',
                'rbhl.context_processors.permissions',
            ],
        },
    },
]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reversion',
    'rest_framework',
    'rest_framework.authtoken',
    'compressor',
    'opal',
    'opal.core.search',
    'opal.core.pathway',
    'legacy',
    'django.contrib.admin',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
    'django_celery_results',
    'plugins.add_patient_step',
    'plugins.lab',
    'rbhl',
)


CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'


V_FORMAT = '%(asctime)s %(process)d %(thread)d %(filename)s %(funcName)s \
%(levelname)s %(message)s'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': V_FORMAT
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'INFO',
            'filters': [],
            'class': 'logging.StreamHandler',
        },
        'console_detailed': {
            'level': 'INFO',
            'filters': [],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'commands': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': True,
        }
    }
}

# Begins custom settings

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DATE_FORMAT = 'd/m/Y'
DATE_INPUT_FORMATS = ['%d/%m/%Y']
DATETIME_FORMAT = 'd/m/Y H:i:s'
DATETIME_INPUT_FORMATS = ['%d/%m/%Y %H:%M:%S']

CSRF_COOKIE_NAME = 'XSRF-TOKEN'
APPEND_SLASH = False

AXES_LOCK_OUT_AT_FAILURE = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend'
)
if not DEBUG:
    EMAIL_HOST_USER = os.environ.get('SENDGRID_USERNAME', '')
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_PASSWORD', '')
else:
    EMAIL_PORT = 1025
    EMAIL_HOST = 'localhost'

COVERAGE_EXCLUDE_MODULES = ('rbhl.migrations', 'rbhl.tests',
                            'rbhl.local_settings',
                            'opal.migrations', 'opal.tests',
                            'opal.wsgi')


# Begins OPAL Settings

OPAL_LOG_OUT_MINUTES = 60
OPAL_LOG_OUT_DURATION = OPAL_LOG_OUT_MINUTES*60*1000

# Begins OPAL optional settings
# OPAL_EXTRA_HEADER = ''
# OPAL_EXTRA_APPLICATION = ''

# Uncomment this to swap out the logo used by this application
# OPAL_LOGO_PATH = 'img/ohc-trans.png'

# Uncomment this if you want to implement custom dynamic flows.
# OPAL_FLOW_SERVICE = 'AppFlow'

INTEGRATING = False

# OPAL required Django settings you should edit

CONTACT_EMAIL = []
DEFAULT_FROM_EMAIL = 'hello@example.com'
DEFAULT_DOMAIN = 'http://rbhl.com/'

# Begins OPAL Settings you should edit !

AUTOCOMPLETE_SEARCH = True
OPAL_BRAND_NAME = 'Indigo'
VERSION_NUMBER  = '1.27'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}


# which views do not require a log in
# if they don't have a name space, its just a string
# otherwise its a string and the name space they are from.
LOGIN_NOT_REQUIRED = (
    # admin login
    ("login", "admin",),

    # two factor core views
    ("login", "two_factor",),
    ("qr", "two_factor",),

    # our two factor views
    "two-factor-setup-redirect",
    "two-factor-required",
    "two-factor-setup",
)

# Django two factor auth settings
LOGIN_URL = 'two_factor:login'
LOGIN_REDIRECT_URL = 'change-password-check'
LOGOUT_REDIRECT_URL = 'two_factor:login'

# the name as it appears in google authenticator
OTP_TOTP_ISSUER = urllib.parse.quote(OPAL_BRAND_NAME)

# Our two factor auth settings

# should super users use two factor authentication
TWO_FACTOR_FOR_SUPERUSERS = True


# if you want sass, uncomment the below and gem install sass
# COMPRESS_PRECOMPILERS = (
#     ('text/x-scss', 'sass --scss {infile} {outfile}'),
# )

if 'test' in sys.argv:
    TWO_FACTOR_FOR_SUPERUSERS = False
else:
    try:
        from rbhl.local_settings import * # noqa
    except ImportError:
        pass
