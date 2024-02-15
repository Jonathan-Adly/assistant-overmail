from pathlib import Path

from environs import Env
from openai import OpenAI

env = Env()
env.read_env()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
"""
Pattern for secrets: Default values are production values, 
and the development values are set in the .env.dev file.
"""


SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = [".spanreed.com", "localhost", "127.0.0.1"]

SITE_URL = env("SITE_URL")
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    # 3rd party
    "allauth",
    "allauth.account",
    "django_celery_beat",
    "whitenoise.runserver_nostatic",
    # local
    "accounts",
]

INTERNAL_IPS = [
    "127.0.0.1",
]
import socket

ip = socket.gethostbyname(socket.gethostname())
INTERNAL_IPS += [ip[:-1] + "1"]

# CRSRF_TRUSTED_ORIGINS = [https://*.website.com]

# production
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=2592000)  # 30 days
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True
)
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
SESSION_COOKIE_SECURE = env.bool("DJANGO_SESSION_COOKIE_SECURE", default=True)
CSRF_COOKIE_SECURE = env.bool("DJANGO_CSRF_COOKIE_SECURE", default=True)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(BASE_DIR.joinpath("templates"))],
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

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": env.dj_db_url("DATABASE_URL", default="postgres://postgres@db/postgres")
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


DEFAULT_FROM_EMAIL = '"Ruby" <ruby@spanreed.com>'
REPLY_TO_EMAIL = "ruby@spanreed.com"

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "mail gun here"
    EMAIL_HOST_USER = "dummy user"
    EMAIL_HOST_PASSWORD = "dummy password"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True


"""
if not DEBUG:
    # sentry
    sentry_sdk.init(
        dsn="https://34052e962c02492587540c790973a6e8@o758170.ingest.sentry.io/4504860459204608",
        integrations=[
            DjangoIntegration(),
        ],
        traces_sample_rate=0.1,
        send_default_pii=True,
    )
"""

# openai
OPENAI_API_KEY = env("openai")

# celery
REDIS_URL = env("REDIS_URL")
CELERY_BROKER_URL = env("REDIS_URL")
CELERY_RESULT_BACKEND = env("REDIS_URL")
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

# stripe
"""
STRIPE_API_KEY = env("STRIPE_API_KEY")
STRIPE_STARTER_PRICE = env("STRIPE_STARTER_PRICE")
STRIPE_PRO_PRICE = env("STRIPE_PRO_PRICE")
STRIPE_STARTER_PRODUCT = env("STRIPE_STARTER_PRODUCT")
STRIPE_PRO_PRODUCT = env("STRIPE_PRO_PRODUCT")
WEBHOOK_SECRET = env("WEBHOOK_SECRET")
"""

# redis cache
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
}

beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Runs every Sunday at 10pm
    "clean_up_sessions": {
        "task": "config.tasks.clean_up",
        "schedule": crontab(day_of_week="sun", hour="22", minute="0"),
    },
}


OPENAI_CLIENT = OpenAI(
    api_key=OPENAI_API_KEY,
)
DEFAULT_GOOD_MODEL = "gpt-3.5-turbo"
DEFAULT_PREMIUM_MODEL = "gpt-4-turbo-preview"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-large"

DEFAULT_PREMIUM_CONFIG = {
    "temperature": 0.25,
    "max_tokens": 2000,
    "frequency_penalty": 0.5,
    "presence_penalty": 0,
    "model": DEFAULT_PREMIUM_MODEL,
}

DEFAULT_GOOD_CONFIG = {
    "temperature": 0.25,
    "max_tokens": 2000,
    "frequency_penalty": 0.5,
    "presence_penalty": 0,
    "model": DEFAULT_GOOD_MODEL,
}

DEFAULT_EMBEDDING_CONFIG = {"model": DEFAULT_EMBEDDING_MODEL, "dimensions": 1024}


# allauth and sesame
SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"
ACCOUNT_SIGNUP_REDIRECT_URL = "home"
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 5
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 86400
ACCOUNT_LOGOUT_REDIRECT_URL = "home"
ACCOUNT_EMAIL_SUBJECT_PREFIX = ""
if DEBUG:
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"
else:
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
AUTH_USER_MODEL = "accounts.CustomUser"
ACCOUNT_LOGOUT_ON_GET = True


# stripe
STRIPE_PUBLIC_KEY = env("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY")
