"""
Django settings for core project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from django.apps import apps

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-=zxta495i_u3l)5focemn58p34t5u+i=469l-c=afhqr#rws89')

DEBUG = os.environ.get('DEBUG', '0') == '1'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',') if os.environ.get('DJANGO_ALLOWED_HOSTS') else ['*'] if DEBUG else []


# Application definition

INSTALLED_APPS = [
    'modeltranslation',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mptt',
    'apps.accounts',
    'apps.categories',
    'apps.publications',
    'apps.subscriptions',
    'apps.website',
]

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

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates' ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.website.context_processors.website_settings',
                'apps.subscriptions.context_processors.subscription_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

if os.environ.get('POSTGRES_DB'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB'),
            'USER': os.environ.get('POSTGRES_USER'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
            'HOST': os.environ.get('POSTGRES_HOST', 'db'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'pt-br'

LANGUAGES = [
    ('pt-br', 'Português'),
    ('en', 'English'),
    ('es', 'Español'),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

MODELTRANSLATION_LANGUAGES = ('pt-br', 'en', 'es')
MODELTRANSLATION_DEFAULT_LANGUAGE = 'pt-br'
MODELTRANSLATION_FALLBACK_LANGUAGES = ('pt-br',)

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [ BASE_DIR / 'static' ]

STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

DATA_UPLOAD_MAX_NUMBER_FILES = 500

CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if os.environ.get('CSRF_TRUSTED_ORIGINS') else []

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

AUTH_USER_MODEL = "accounts.User"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'] if not DEBUG else ['console'],
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['console', 'file'] if not DEBUG else ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

#Email Backend
EMAIL_BACKEND=os.environ.get('EMAIL_BACKEND', '')
EMAIL_HOST=os.environ.get('EMAIL_HOST', '')
EMAIL_PORT=os.environ.get('EMAIL_PORT', 587)
EMAIL_USE_TLS=os.environ.get('EMAIL_USE_TLS', True)
EMAIL_HOST_USER=os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD=os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL=os.environ.get('DEFAULT_FROM_EMAIL', '')

#Login redirect
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'publications:home'
LOGOUT_REDIRECT_URL = 'publications:home'

#Email verification timeout (24 hours in seconds)
PASSWORD_RESET_TIMEOUT = 86400

#Stripe
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
STRIPE_CURRENCY = 'usd'

def get_dynamic_logo():
    try:
        WebsiteModel = apps.get_model('website', 'WebSettings')
        config = WebsiteModel.objects.first()
        if config and config.logo:
            return '..' + config.logo.url
    except Exception:
        pass
    return "img/default-logo.png"

JAZZMIN_SETTINGS = {
    "site_title": "Pubfiles",
    "site_header": "Pubfiles",
    "site_brand": "Admin Panel",
    "welcome_sign": "Welcome!",
    "copyright": "VWTech Dev",
    "search_model": ["accounts.User"],
    "site_logo": get_dynamic_logo,
    "login_logo_styles": "width: 30px; height: 30px; margin-bottom: 5px; display: block; margin-left: auto; margin-right: auto;",
    "site_logo_classes": "img-fluid",
    "changeform_format": "horizontal_tabs",
    "topmenu_links": [
        {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Ver Site", "url": "publications:home", "new_window": True},
    ],
    "icons": {
        "accounts": "fas fa-users-cog",
        "accounts.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "publications.publication": "fas fa-book",
        "categories.category": "fas fa-tags",
        "subscriptions.subscription": "fas fa-crown",
        "subscriptions.subscriptionsettings": "fas fa-cog",
        "website.website": "fas fa-globe",
    },
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-primary",
    "navbar": "navbar-dark navbar-black",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_options": {
        "dark_mode_toggle": True
    },
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}
