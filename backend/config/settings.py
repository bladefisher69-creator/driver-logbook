import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from corsheaders.defaults import default_headers

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-change-this-in-production')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_yasg',
    'django_filters',
    'logbook',
    'channels',
]

# Use the custom Driver model as the project's user model to avoid clashes
# with the default auth.User model's related names for groups and permissions.
AUTH_USER_MODEL = 'logbook.Driver'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

# If using Channels, ASGI application is set in config.asgi.application
ASGI_APPLICATION = 'config.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'driver_logbook'),
        'USER': os.getenv('DB_USER', 'logbook_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'soeVpvzdt6QkM95i'),
        'HOST': os.getenv('DB_HOST', 'driver_logbook-us-southeast-18421.kloudbeansite.com'),
        'PORT': os.getenv('DB_PORT', '33096'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'connect_timeout': 300,   # Timeout in seconds (5 minutes)
            'init_command': "SET SESSION wait_timeout=28800, SESSION interactive_timeout=28800",
        }
    }
}
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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

if DEBUG:
    CORS_ALLOWED_ORIGINS = [
        'http://localhost:5173',
        'http://localhost:5174',
    ]
else:
    # Default static allowed origins (kept for safety).
    DEFAULT_CORS_ORIGINS = [
        'https://driver-logbook-zeta.vercel.app',
        'https://driver-logbook-git-main-bladefisher69-creators-projects.vercel.app',
        'https://driver-logbook-27j6a5smp-bladefisher69-creators-projects.vercel.app',
        'https://driver-logbook-silk.vercel.app',
        'https://driver-logbook-6b2dvm5yo-bladefisher69-creators-projects.vercel.app',
        'https://driver-logbook-1t3y.onrender.com',
        # Legacy / alternate backend hostname some frontends still call
        'https://driver-logbook.onrender.com',
    ]

    # Allow overriding or extending allowed origins via an environment variable
    # CORS_ALLOWED_ORIGINS_ENV should be a comma-separated list of origins,
    # e.g. "https://example.com,https://staging.example.com"
    def _parse_env_origins(env_value: str | None):
        if not env_value:
            return []
        return [o.strip() for o in env_value.split(',') if o.strip()]

    env_origins = _parse_env_origins(os.getenv('CORS_ALLOWED_ORIGINS_ENV'))
    # If a simple replacement is desired, set CORS_OVERRIDE_ALLOW_ALL to 'True'
    # and provide CORS_ALLOWED_ORIGINS_ENV; otherwise, we merge defaults + env.
    if os.getenv('CORS_OVERRIDE_ALLOW_ALL', 'False') == 'True' and env_origins:
        CORS_ALLOWED_ORIGINS = env_origins
    else:
        # Merge defaults with env provided origins (env takes precedence for duplicates)
        CORS_ALLOWED_ORIGINS = list(dict.fromkeys(DEFAULT_CORS_ORIGINS + env_origins))

# Allow credentials in cross-site requests (cookies, auth headers)
CORS_ALLOW_CREDENTIALS = True

# In addition to explicit origins, allow Vercel preview/deployment subdomains
# using a regex. This is intentionally conservative: only allow https subdomains
# of vercel.app. We also expose the primary render domain.
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https:\/\/.*\.vercel\.app$",
    r"^https:\/\/driver-logbook(?:-\w+)?\.onrender\.com$",
]

# Trusted origins for CSRF checks (mirrors the production allowed origins).
CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
    "https://driver-logbook.onrender.com",
    "https://driver-logbook-1t3y.onrender.com",
]

# Merge default CORS request headers with Django CORS defaults
CORS_ALLOW_HEADERS = list(default_headers) + [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Allowed HTTP methods for CORS preflight
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]


HOURS_LIMIT_8_DAYS = 70
REFUEL_MILES_LIMIT = 1000
PICKUP_TIME_HOURS = 1
DROPOFF_TIME_HOURS = 1

# Channels / Redis settings (used for real-time features)
REDIS_URL = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379')
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    },
}
