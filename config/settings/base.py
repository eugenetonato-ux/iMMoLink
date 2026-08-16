"""
Django settings for config project — commun à tous les environnements.

DEBUG, ALLOWED_HOSTS, EMAIL_BACKEND et les réglages de sécurité HTTPS
sont définis dans dev.py / prod.py, pas ici.
"""
from pathlib import Path
from decouple import config

# settings/base.py -> settings/ -> config/ -> racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")
CURRENCY = config("CURRENCY", default="XOF")
PLATFORM_NAME = config("PLATFORM_NAME", default="iMMoLink")
ADMIN_URL_PATH = config("ADMIN_URL_PATH", default="cpanel_administrateur")

# Espace admin séparé (jamais un compte utilisateur classique / jamais allauth)
ADMIN_USERNAME = config("ADMIN_USERNAME", default="")
ADMIN_PASSWORD = config("ADMIN_PASSWORD", default="")
ADMIN_TOTP_SECRET = config("ADMIN_TOTP_SECRET", default="")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # Tiers
    "rest_framework",
    "corsheaders",
    "django_filters",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    # Apps iMMoLink
    "apps.accounts",
    "apps.properties",
    "apps.locations",
    "apps.favorites",
    "apps.payments",
    "apps.notifications",
    "apps.adminpanel",
    "apps.api",
    "apps.common",
    "apps.website",
    "apps.geo",
]

SITE_ID = 1

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.common.context_processors.platform",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
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
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Porto-Novo"
USE_I18N = True
USE_TZ = True


# Email — EMAIL_BACKEND défini par environnement (dev.py / prod.py)
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="")
ADMIN_NOTIFICATION_EMAIL = config("ADMIN_NOTIFICATION_EMAIL", default="")

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

AUTH_USER_MODEL = "accounts.User"

LOGIN_URL = "/compte/connexion/"
LOGIN_REDIRECT_URL = "/compte/choix-role/"
LOGOUT_REDIRECT_URL = "/"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "APPS": [
            {
                "client_id": config("GOOGLE_OAUTH_CLIENT_ID"),
                "secret": config("GOOGLE_OAUTH_CLIENT_SECRET"),
                "key": "",
            }
        ],
    }
}

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="", cast=lambda v: [s.strip() for s in v.split(",") if s])

# --- Sebpay (paiements Mobile Money) ---
SEBPAY_API_KEY = config("SEBPAY_API_KEY", default="")
SEBPAY_API_URL = config("SEBPAY_API_URL", default="")  # URL exacte de l'endpoint, à copier depuis ton dashboard Sebpay
SEBPAY_WEBHOOK_URL = config("SEBPAY_WEBHOOK_URL", default="")
SEBPAY_WEBHOOK_SECRET = config("SEBPAY_WEBHOOK_SECRET", default="")
SEBPAY_SIGNATURE_HEADER = config("SEBPAY_SIGNATURE_HEADER", default="X-Sebpay-Signature")
SEBPAY_API_URL = config("SEBPAY_API_URL", default="https://newapi.sebpay.bj/api/v1/collections")