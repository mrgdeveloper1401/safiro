import os
from datetime import timedelta
from pathlib import Path
from decouple import config, Csv
from django.utils import timezone

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', cast=str, default='hello_world')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv(), default="")

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
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "django_extensions",

    # third party app
    "auth_app"
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
        'DIRS': [],
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
        "PORT": config("POSTDB_PORT", cast=int, default=5434),
        "CONN_MAX_AGE": config("POSTDB_CONN_MAX_AGE", cast=int, default=300),
        # "DISABLE_SERVER_SIDE_CURSORS": config("DISABLE_SERVER_SIDE_CURSORS", cast=bool, default=False),
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = config("TIME_ZONE", cast=str, default="UTC")

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static' # when manage.py collect-static save static files

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
    AWS_QUERYSTRING_AUTH = False
    AWS_ACCESS_KEY_ID = config('S3_ACCESS_KEY', cast=str)
    AWS_SECRET_ACCESS_KEY = config('S3_SECRET_KEY', cast=str)
    AWS_STORAGE_BUCKET_NAME = config('S3_BUCKET_NAME', cast=str)
    AWS_S3_ENDPOINT_URL = config('S3_BUCKET_URL', cast=str)
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_MAX_MEMORY_SIZE = 1024 * 1024 * 2
else:
    MEDIA_ROOT = BASE_DIR / 'media'  # upload file into dir
    MEDIA_URL = '/media/'  # address in url

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# rest framework
# rest config
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_RATES': {
        'otp': '1/minute',
    },
}

# config debug toolbar
SHOW_DEBUGGER_TOOLBAR = config("SHOW_DEBUGGER_TOOLBAR", cast=bool, default=True)
if SHOW_DEBUGGER_TOOLBAR:
    INSTALLED_APPS += [
        "debug_toolbar"
    ]
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware"
    ]
    INTERNAL_IPS = ["127.0.0.1"]


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
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "CONNECTION_POOL_KWARGS": {"max_connections": 100, "retry_on_timeout": True},
        },
        "KEY_PREFIX": "safiro",
    }
}
if DEBUG:
    CACHES['default']['LOCATION'] = "redis://localhost:6381/1"
else:
    CACHES['default']['LOCATION'] = config("PRODU_REDIS_LOCATION", cast=str)

# config package corsheaders
if DEBUG is False:
    CORS_ALLOWED_ORIGINS = config("PRODUCTION_CORS_ALLOWED_ORIGINS", cast=Csv())

# config session cache
SESSION_ENGINE = "django.contrib.sessions.backends.cache"

# whitenoise
USE_WHITENOISE = config("USE_WHITENOISE", cast=bool, default=True)
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
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=config("ACCESS_TOKEN_LIFETIME", cast=int, default=1200)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=config("REFRESH_TOKEN_LIFETIME", cast=int, default=30)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": config("SIGNING_KEY", cast=str, default="test_project"),
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": config("ISSUER", cast=str, default="127.0.0.1:8000"),
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

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
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
