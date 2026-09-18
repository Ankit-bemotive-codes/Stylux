

import os
from pathlib import Path

from dotenv import load_dotenv


''' Load environment variables from .env file'''

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
GEMINI_TIMEOUT = int(os.getenv("GEMINI_TIMEOUT", "30000"))

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-development-key")
DEBUG = os.getenv("DEBUG", "True").lower() in {"1", "true", "yes", "on"}
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'ai',
    
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'application.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'application.wsgi.application'


# Database
# Local MySQL configuration for the fresh database created in MySQL Workbench.
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'eapp',
        'USER': 'root',
        'PASSWORD': '654321',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'core' / 'static']
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}

# media files (user-uploaded files)
MEDIA_URL = '/Media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'Media')

#RAZOR PAY PYPE LINE
RAZORPAY_KEY_ID = 'rzp_test_TXZmC54IbH8ksa'
RAZORPAY_KEY_SECRET='RnMUpOmlDNLJe2o2BQkTveMO'
