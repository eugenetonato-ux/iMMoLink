"""
Settings de production.

À activer explicitement via :
DJANGO_SETTINGS_MODULE=config.settings.prod
"""

from decouple import config

from .base import *  # noqa: F401,F403


# ============================================================
# PRODUCTION
# ============================================================

DEBUG = False


# ============================================================
# HOSTS
# ============================================================

ALLOWED_HOSTS = [
    host.strip()
    for host in config("ALLOWED_HOSTS", default="").split(",")
    if host.strip()
]


# ============================================================
# CSRF
# ============================================================

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="",
    cast=lambda v: [
        s.strip()
        for s in v.split(",")
        if s.strip()
    ],
)


# ============================================================
# EMAIL
# ============================================================

EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
)


# ============================================================
# SÉCURITÉ HTTPS
# ============================================================

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_HSTS_PRELOAD = True

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"


# Render termine HTTPS avant de transmettre
# la requête à Django.
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)


# ============================================================
# CACHE PARTAGÉ
# ============================================================

CACHES = {
    "default": {
        "BACKEND": (
            "django.core.cache.backends.db.DatabaseCache"
        ),
        "LOCATION": "django_cache_table",
    }
}