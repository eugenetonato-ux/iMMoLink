"""
Django settings for config project — commun à tous les environnements.

DEBUG, ALLOWED_HOSTS, EMAIL_BACKEND et les réglages de sécurité HTTPS
sont définis dans dev.py / prod.py, pas ici.
"""

from pathlib import Path

import dj_database_url
from decouple import config


# settings/base.py -> settings/ -> config/ -> racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")
CURRENCY = config("CURRENCY", default="XOF")
PLATFORM_NAME = config("PLATFORM_NAME", default="iMMoLink")
ADMIN_URL_PATH = config(
    "ADMIN_URL_PATH",
    default="cpanel_administrateur",
)

# Espace admin séparé
ADMIN_USERNAME = config("ADMIN_USERNAME", default="")
ADMIN_PASSWORD = config("ADMIN_PASSWORD", default="")
ADMIN_TOTP_SECRET = config("ADMIN_TOTP_SECRET", default="")


# ============================================================
# APPLICATIONS
# ============================================================

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


# ============================================================
# MIDDLEWARE
# ============================================================

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


# ============================================================
# TEMPLATES
# ============================================================

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


# ============================================================
# DATABASE
# ============================================================
#
# Localement :
#   SQLite si DATABASE_URL n'existe pas.
#
# Sur Render :
#   PostgreSQL si DATABASE_URL est définie.
#

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ============================================================
# INTERNATIONALISATION
# ============================================================

LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Porto-Novo"
USE_I18N = True
USE_TZ = True


# ============================================================
# EMAIL
# ============================================================

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="")
ADMIN_NOTIFICATION_EMAIL = config(
    "ADMIN_NOTIFICATION_EMAIL",
    default="",
)


# ============================================================
# AUTHENTIFICATION
# ============================================================

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

AUTH_USER_MODEL = "accounts.User"

LOGIN_URL = "/compte/connexion/"
LOGIN_REDIRECT_URL = "/compte/choix-role/"
LOGOUT_REDIRECT_URL = "/"


# ============================================================
# GOOGLE OAUTH
# ============================================================

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


# ============================================================
# STATIC / MEDIA
# ============================================================

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.PageNumberPagination"
    ),
    "PAGE_SIZE": 20,
}


# ============================================================
# CORS
# ============================================================

CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="",
    cast=lambda v: [
        s.strip()
        for s in v.split(",")
        if s.strip()
    ],
)


# ============================================================
# SEBPAY — PAIEMENTS MOBILE MONEY
# ============================================================

SEBPAY_SECRET_KEY = config(
    "SEBPAY_SECRET_KEY",
    default="",
)

SEBPAY_API_URL = config(
    "SEBPAY_API_URL",
    default=(
        "https://newapi.sebpay.bj/"
        "api/v1/collections"
    ),
)

SEBPAY_WEBHOOK_URL = config(
    "SEBPAY_WEBHOOK_URL",
    default="",
)

SEBPAY_SIGNATURE_HEADER = config(
    "SEBPAY_SIGNATURE_HEADER",
    default="X-Sebpay-Signature",
)