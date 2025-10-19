import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from corsheaders.defaults import default_headers

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-change-this-in-production')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

def _env_list(name: str, default: str = ''):
    """Return a list from a comma-separated environment variable.
    Example: 'a.com, b.com' -> ['a.com', 'b.com']
    If the env var is empty, returns an empty list (or splits the default).
    """
    val = os.getenv(name, default)
    if val is None:
        return []
    # If the entire value is a single '*', return ['*'] to allow wildcard
    if val.strip() == '*':
        return ['*']
    return [p.strip() for p in val.split(',') if p.strip()]


# ALLOWED_HOSTS: set via environment variable (comma-separated). Default to ['*'] if not provided.
raw_allowed = os.getenv('ALLOWED_HOSTS', '*')
if raw_allowed.strip() == '*':
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = _env_list('ALLOWED_HOSTS', raw_allowed)

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


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
    # Local dev origins for Vite
    CORS_ALLOWED_ORIGINS = [
        'http://localhost:5173',
        'http://localhost:5174',
    ]
else:
    # Production origins should be provided via the CORS_ALLOWED_ORIGINS env var as a comma-separated list.
    # Example (set on Render):
    # CORS_ALLOWED_ORIGINS=https://app.yourdomain.com,https://driver-logbook-nine.vercel.app,https://driver-logbook-git-main-bladefisher69-creators-projects.vercel.app
    CORS_ALLOWED_ORIGINS = _env_list('CORS_ALLOWED_ORIGINS', '')

CORS_ALLOW_CREDENTIALS = True

# CSRF trusted origins - allow overriding via environment variable (comma-separated)
raw_csrf_trusted = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if raw_csrf_trusted:
    CSRF_TRUSTED_ORIGINS = [d.strip() for d in raw_csrf_trusted.split(',') if d.strip()]
else:
    # sensible defaults for known production frontends (adjust as needed)
    CSRF_TRUSTED_ORIGINS = [
        'https://driver-logbook-m7e5.vercel.app',
    ]

# Cookie security settings: Render terminates TLS at edge, so mark cookies secure in prod
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True') == 'True'
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'True') == 'True'

# SameSite handling: use 'None' for cross-site cookies (requires Secure=True)
SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'None')
CSRF_COOKIE_SAMESITE = os.getenv('CSRF_COOKIE_SAMESITE', 'None')

# Add this right after CORS_ALLOWED_ORIGINS and CORS_ALLOW_CREDENTIALS
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
