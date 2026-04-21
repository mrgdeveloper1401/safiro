import os
from datetime import timedelta
from pathlib import Path

from clickhouse_connect import get_client
from decouple import config, Csv
from django.utils import timezone
from kombu import Queue

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', cast=str, default='hello_world')

# secret key fall back
USE_FALL_BACK_SECRET_KEY = config('USE_FALL_BACK_SECRET_KEY', cast=bool, default=False)
if USE_FALL_BACK_SECRET_KEY:
    DJANGO_SECRET_KEY_FALLBACKS = config('DJANGO_SECRET_KEY_FALLBACKS', cast=str)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv(), default="*")

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # third_party package,
    'rest_framework',
    'rest_framework_simplejwt',
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "django_extensions",
    "django_filters",

    # third party app
    "apps.auth_app.apps.AuthAppConfig",
    "apps.core_app.apps.CoreAppConfig",
    "apps.trip_app.apps.TripAppConfig",
    "apps.shop_app.apps.ShopAppConfig",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'base.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

USE_ASGI = config('USE_ASGI', default=True, cast=bool)
if USE_ASGI:
    ASGI_APPLICATION = 'base.asgi.application'
else:
    WSGI_APPLICATION = 'base.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": config("PGDB_ENGINE", default="django.db.backends.postgresql", cast=str),
        "NAME": config("POSTDB_NAME", cast=str, default="safiro"),
        "USER": config("POSTDB_USER", cast=str, default="postgres"),
        "PASSWORD": config("POSTDB_PASSWORD", cast=str, default="postgres"),
        "HOST": config("POSTDB_HOST", cast=str, default="127.0.0.1"),
        "PORT": config("POSTDB_PORT", cast=int, default=5433),
        "CONN_MAX_AGE": config("POSTDB_CONN_MAX_AGE", cast=int, default=60), #
        "CONN_HEALTH_CHECKS": config("POSTDB_CONN_HEALTH_CHECKS", cast=bool, default=True)
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = config("LANGUAGE_CODE", cast=str, default="en-us")

TIME_ZONE = config("TIME_ZONE", cast=str, default="UTC")

USE_I18N = config("USE_I18N", default=True, cast=bool)

USE_TZ = config("USE_TZ", default=True, cast=bool)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # when manage.py collect-static save static files
# STATICFILES_DIRS = [BASE_DIR / "static"]

# config storages
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}
}


USE_DJANGO_STORAGES = config("USE_DJANGO_STORAGES", cast=bool, default=False)
if USE_DJANGO_STORAGES:
    STORAGES['default']['BACKEND'] = 'storages.backends.s3.S3Storage'
    AWS_S3_REGION_NAME = 'eu-west-1'
    AWS_DEFAULT_ACL = 'public-read'
    AWS_QUERYSTRING_AUTH = config("AWS_QUERYSTRING_AUTH", default=False, cast=bool)
    AWS_ACCESS_KEY_ID = config('S3_ACCESS_KEY', cast=str)
    AWS_SECRET_ACCESS_KEY = config('S3_SECRET_KEY', cast=str)
    AWS_STORAGE_BUCKET_NAME = config('S3_BUCKET_NAME', cast=str)
    AWS_S3_ENDPOINT_URL = config('S3_BUCKET_URL', cast=str)
    AWS_S3_FILE_OVERWRITE = config('S3_FILE_OVERWRITE', cast=bool, default=False)
    AWS_S3_MAX_MEMORY_SIZE = config('S3_MAX_MEMORY_SIZE', cast=int, default=2097152)
else:
    MEDIA_ROOT = BASE_DIR / 'media'  # upload file into dir
    MEDIA_URL = '/media/'  # address in url

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = config("DEFAULT_AUTO_FIELD", cast=str, default="django.db.models.BigAutoField")

# rest framework
# rest config
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_RATES': {
        'otp': '1/minute', #TODO, bug fix send otp every 2minute
    },
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend']
}

# config debug toolbar
SHOW_DEBUGGER_TOOLBAR = config("SHOW_DEBUGGER_TOOLBAR", cast=bool, default=True)
if DEBUG and SHOW_DEBUGGER_TOOLBAR:
    INSTALLED_APPS += [
        "debug_toolbar"
    ]
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware"
    ]
    INTERNAL_IPS = ("127.0.0.1",)


USE_SSL_CONFIG = config("USE_SSL_CONFIG", cast=bool, default=False)
if USE_SSL_CONFIG:
    # Https/ssl settings
    SECURE_SSL_REDIRECT = True # redirect http request into https request
    USE_X_FORWARDED_HOST = True # use header x-forwarded-host
    USE_X_FORWARDED_PORT = True # use header x-forwarded-port

    # HSTS settings
    SECURE_HSTS_SECONDS = 31536000  # 1 year, hsts validity period
    SECURE_HSTS_PRELOAD = True #
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True # active hsts into subdomain

    # cookie
    SESSION_COOKIE_SECURE = True # session cookie only https
    SESSION_COOKIE_DOMAIN = config("SESSION_COOKIE_DOMAIN", cast=str) # for example --> .example.com, domain cookie
    SESSION_COOKIE_HTTPONLY = True # prevent access with by javascript

    # csrf
    CSRF_COOKIE_SECURE = True # send cookie csrf only https
    CSRF_COOKIE_HTTPONLY = True # csrf prevent access javascript
    CSRF_COOKIE_SAMESITE = 'Strict' # Prevent cookie requests on cross-site requests
    CSRF_COOKIE_DOMAIN = config("CSRF_COOKIE_DOMAIN", cast=str) # for example --> .example.com, domain csrf cookie
    CSRF_COOKIE_AGE = 3600 # csrf cookie validity period

    # Content Security Settings
    SECURE_CONTENT_TYPE_NOSNIFF = True # prevent mime sniffing
    SECURE_BROWSER_XSS_FILTER = True # active filter xss in browser
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin" # control information  on sourse request
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Frame & Clickjacking Protection
    X_FRAME_OPTIONS = "DENY" # prevent show iframe

# cache config
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_LOCATION", cast=str, default="redis://localhost:6381/1"),
        "OPTIONS": {
            "SERIALIZER": config("REDIS_DEFAULT_SERIALIZER", cast=str, default="django_redis.serializers.msgpack.MSGPackSerializer"),
            "SOCKET_CONNECT_TIMEOUT": config("SOCKET_DEFAULT_CONNECT_TIMEOUT", default=5, cast=int),
            "SOCKET_TIMEOUT": config("SOCKET_DEFAULT_TIMEOUT", default=5, cast=int),
            "COMPRESSOR": config("REDIS_DEFAULT_COMPRESSOR", default="django_redis.compressors.zlib.ZlibCompressor"),
            "TIMEOUT": config("CACHE_DEFAULT_TIMEOUT", cast=int, default=1209600),
            "COMPRESSOR_KWARGS": {
                "level": config("COMPRESSOR_DEFAULT_LEVEL_ARGS", default=5, cast=int)
            },
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": config("REDIS_MAX_CONNECTION", cast=int, default=30),
                "retry_on_timeout": config("REDIS_DEFAULT_POOL_RETRY_TIMEOUT", default=True, cast=bool),
                "health_check_interval": config("REDIS_DEFAULT_HEALTH_CHECK_INTERVAL", default=True, cast=bool),
                "socket_keepalive": config("REDIS_DEFAULT_SOCKET_KEEPALIVE", default=True, cast=bool),
            }
        }
    }
}

# config package corsheaders
USE_CROS = config("USE_CROS", cast=bool, default=False)
if not DEBUG and USE_CROS:
    CORS_ALLOWED_ORIGINS = config("PRODUCTION_CORS_ALLOWED_ORIGINS", cast=Csv())

# config session cache
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = config("SESSION_CACHE_ALIAS", cast=str, default="default")

# whitenoise
USE_WHITENOISE = config("USE_WHITENOISE", cast=bool, default=False)
if USE_WHITENOISE:
    MIDDLEWARE += [
        "whitenoise.middleware.WhiteNoiseMiddleware"
    ]
    STORAGES['staticfiles']['BACKEND'] = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# config log
USE_LOG = config("USE_LOG", cast=bool, default=True)
if USE_LOG:
    log_dir = os.path.join('general_log_django', timezone.now().strftime("%Y-%m-%d"))
    os.makedirs(log_dir, exist_ok=True)
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "color": {
                "()": "colorlog.ColoredFormatter",
                "format": "%(log_color)s%(levelname)s %(reset)s%(asctime)s %(module)s %(process)d %(thread)d %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "error_file": {
                "level": "ERROR",
                "class": "logging.FileHandler",
                "formatter": "color",
                "filename": os.path.join(log_dir, 'error_file.log')
            },
            "warning_file": {
                "level": "WARN",
                "class": "logging.FileHandler",
                "formatter": "color",
                "filename": os.path.join(log_dir, 'warning_file.log')
            },
            "critical_file": {
                "level": "CRITICAL",
                "class": "logging.FileHandler",
                "formatter": "color",
                "filename": os.path.join(log_dir, 'critical_file.log')
            },
        },
        "loggers": {
            "django": {
                "handlers": ["warning_file", "critical_file", "error_file"],
                'propagate': True,
            }
        }
    }

# jwt config
SIMPLE_JWT = {
    "REFRESH_TOKEN_LIFETIME": timedelta(days=config("REFRESH_TOKEN_LIFETIME", cast=int, default=365)),
    "ACCESS_TOKEN_LIFETIME": timedelta(days=config("ACCESS_TOKEN_LIFETIME", cast=int, default=7)),
    "ALGORITHM": "HS256",
    "SIGNING_KEY": config("SIGNING_KEY", cast=str, default="test_project"),
    "VERIFYING_KEY": "",
    "AUDIENCE": config("AUDIENCE", cast=str, default=None),
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "ROTATE_REFRESH_TOKENS": config("ROTATE_REFRESH_TOKENS", cast=bool, default=True),
    "BLACKLIST_AFTER_ROTATION": config("BLACKLIST_AFTER_ROTATION", cast=bool, default=True),
    "UPDATE_LAST_LOGIN": config("UPDATE_LAST_LOGIN", cast=bool, default=True),
}

# swagger config
SPECTACULAR_SETTINGS = {
    'TITLE': 'Your Project API',
    'DESCRIPTION': 'Your project description',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # OTHER SETTINGS
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
}

# SPECTACULAR_EXTRAS_SETTINGS
USE_SPECTACULAR_EXTRAS_SETTINGS = config("USE_SPECTACULAR_EXTRAS_SETTINGS", cast=bool, default=True)
if USE_SPECTACULAR_EXTRAS_SETTINGS:
    INSTALLED_APPS += [
        "drf_spectacular_extras",
    ]

    SPECTACULAR_EXTRAS_SETTINGS = {
        'SCALAR_UI_SETTINGS': {
            'theme': 'purple',
            'layout': 'modern',
            'showSidebar': True,
            'hideDownloadButton': False,
            'searchHotKey': 'k',
            # Add any Scalar configuration options
        },
    }

# custom user model
AUTH_USER_MODEL = 'auth_app.User'

# celery config
USE_CELERY = config("USE_CELERY", cast=bool, default=True)
if USE_CELERY:
    CELERY_BROKER_URL = config('CELERY_BROKER_URL', cast=str, default="redis://localhost:6381/5")
    CELERY_TIMEZONE = config("CELERY_TIMEZONE", cast=str, default=TIME_ZONE)
    CELERY_ACCEPT_CONTENT = config("CELERY_ACCEPT_CONTENT", cast=Csv(), default="json")
    CELERY_TASK_SERIALIZER = config("CELERY_TASK_SERIALIZER", cast=str, default="json")
    CELERY_RESULT_SERIALIZER = config("CELERY_RESULT_SERIALIZER", cast=str, default="json")
    CELERY_TASK_ACKS_LATE = config("CELERY_TASK_ACKS_LATE", cast=bool, default=True)
    CELERY_WORKER_PREFETCH_MULTIPLIER = config("WORKER_PREFETCH_MULTIPLIER", cast=int, default=1)
    CELERY_TASK_ALWAYS_EAGER = config("CELERY_TASK_ALWAYS_EAGER", cast=bool, default=False)
    CELERY_TASK_TIME_LIMIT = config("CELERY_TASK_TIME_LIMIT", cast=int, default=20)
    CELERY_ENABLE_UTC = config("CELERY_ENABLE_UTC", cast=bool, default=True)
    CELERY_WORKER_CONCURRENCY = config("WORKER_CONCURRENCY", cast=int, default=os.cpu_count())
    CELERY_WORKER_MAX_TASKS_PER_CHILD = config("WORKER_MAX_TASKS_PER_CHILD", cast=int, default=1000)
    CELERY_WORKER_MAX_MEMORY_PER_CHILD = config("WORKER_MAX_MEMORY_PER_CHILD", cast=int, default=200000)

    # celery queue
    CELERY_TASK_QUEUES = (
        Queue("send_otp"),
        Queue("shop_event")
    )

# use email
USE_EMAIL = config("USE_EMAIL", cast=bool, default=False)
if USE_EMAIL:
    ADMINS = config("ADMINS", cast=Csv())
    EMAIL_BACKEND = config("EMAIL_BACKEND", cast=str, default="django.core.mail.backends.console.EmailBackend")
    EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", cast=str)
    EMAIL_HOST = config("EMAIL_HOST", cast=str, default="smtp.gmail.com")
    EMAIL_PORT = config("EMAIL_PORT", cast=int, default=587)
    EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=True)
    EMAIL_HOST_USER = config("EMAIL_HOST_USER", cast=str)

# use clickhouse database
USE_CLICKHOUSE_DB = config("USE_CLICKHOUSE_DB", cast=bool, default=True)
if USE_CLICKHOUSE_DB:
    CLICKHOUSE_DB_HOST = config("CLICKHOUSE_DB_HOST", cast=str, default="localhost")
    CLICKHOUSE_DB_PORT = config("CLICKHOUSE_DB_PORT", cast=int, default=8123)
    CLICKHOUSE_DB_USER = config("CLICKHOUSE_DB_USER", cast=str, default="new_user")
    CLICKHOUSE_DB_PASSWORD = config("CLICKHOUSE_DB_PASSWORD", cast=str, default="new_password")
    CLICKHOUSE_DB_DATABASE = config("CLICKHOUSE_DB_DATABASE", cast=str, default="default")
