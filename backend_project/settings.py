from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta
import datetime
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1', 'localhost',
    '192.168.1.38', '.vercel.app',
    '.now.sh', '.thoughtforest.xyz',
    'vrec.onrender.com',
    ]

AUTH_USER_MODEL = 'api_app.User'

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "api_app",
    "rest_framework",
    "corsheaders",
    "rest_framework.authtoken",
]

REST_FRAMEWORK = {
     'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
      ],
}

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=10),  # Set the token expiration
}

# settings.py

# Celery Configuration
CORS_ORIGIN_ALLOW_ALL=True
CORS_ALLOW_CREDENTIALS=False
SIMPLE_JWT = {
     'ACCESS_TOKEN_LIFETIME': timedelta(minutes=10),
     'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
     'ROTATE_REFRESH_TOKENS': True,
     'BLACKLIST_AFTER_ROTATION': True
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')


ROOT_URLCONF = "backend_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend_project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    #     'OPTIONS': {'charset': 'utf8mb4'},
    # },
    'default': {
        'ENGINE': 'django_psdb_engine',
        'NAME': os.environ.get('DB_NAME'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'OPTIONS': {
            'ssl': {
                'ca': os.environ.get('MYSQL_ATTR_SSL_CA_LOCAL_DEMO'),
                }
        }
  }
}

# DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)
# DATABASES['default']['OPTIONS']['charset'] = 'utf8mb4'
# del DATABASES['default']['OPTIONS']['sslmode'] 
# DATABASES['default']['OPTIONS']['ssl'] =  {'ca': os.environ.get('MYSQL_ATTR_SSL_CA')}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": 
        "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER') #email-id associated with above host
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD') #password for above email-id
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), ]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')