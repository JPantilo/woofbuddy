from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-ees7*pk@3s*#^6=h05*7bgsri0q-6nh9&v_y-3putg19q3^iu5'

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*', '.onrender.com', '127.0.0.1', 'localhost']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',
    'appointments.apps.AppointmentsConfig',
    'payments.apps.PaymentsConfig',
    'communications.apps.CommunicationsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'grooming.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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


WSGI_APPLICATION = 'grooming.wsgi.application'

import dj_database_url

# Database Configuration
# Use PostgreSQL on Render, SQLite locally
if 'DATABASE_URL' in os.environ:
    # Production: Render PostgreSQL
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Development: Local SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# PayPal Configuration
PAYPAL_MODE = os.environ.get('PAYPAL_MODE', 'sandbox')
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', 'AY7mFMLsEaWYxtXDFsdB2V9RgQWzXLnKoWguilGlKjaSEyYgpHc4WOBnhHNolC_LW0UTAkQKTT2LRNU4')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET', 'EHmZAY2axRgeBmnD5d19DmK2Mp93aEK4zf_txpLxukFLsIkeSZdj1JwgPy4wgtSb2hLy6dJTYAtoDSpS')
PAYPAL_RECEIVER_EMAIL = os.environ.get('PAYPAL_RECEIVER_EMAIL', 'sb-xxxxxx@business.example.com')
PAYPAL_RETURN_URL = os.environ.get('PAYPAL_RETURN_URL', 'https://woofbuddy.onrender.com/payments/paypal/return/')
PAYPAL_CANCEL_URL = os.environ.get('PAYPAL_CANCEL_URL', 'https://woofbuddy.onrender.com/payments/paypal/cancel/')
PAYPAL_NOTIFY_URL = os.environ.get('PAYPAL_NOTIFY_URL', 'https://woofbuddy.onrender.com/payments/paypal/notify/')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'Woof Buddy Pet Grooming <your-email@gmail.com>'
ADMIN_EMAIL = 'your-email@gmail.com'
EMAIL_SUBJECT_PREFIX = '[Woof Buddy] '
SERVER_EMAIL = EMAIL_HOST_USER

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

# Custom User Model
AUTH_USER_MODEL = 'users.User'
