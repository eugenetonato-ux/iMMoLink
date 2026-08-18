"""
Settings de production. À activer explicitement via
DJANGO_SETTINGS_MODULE=config.settings.prod (jamais par défaut).
"""
from decouple import config

from .base import *  # noqa: F401,F403

DEBUG = True
print("=== PROD SETTINGS LOADED ===")
print("DEBUG =", DEBUG)
print("ALLOWED_HOSTS =", ALLOWED_HOSTS)
print("CSRF_TRUSTED_ORIGINS =", CSRF_TRUSTED_ORIGINS)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="").split(",")

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="",
    cast=lambda v: [s.strip() for s in v.split(",") if s],
)

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# --- Sécurité HTTPS / cookies (requis avant toute mise en ligne réelle) ---
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Décommente si le site est derrière un proxy/load balancer (Nginx, Render, etc.)
# qui termine le HTTPS avant d'atteindre Django :
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# --- Cache partagé (base de données) ---
# Important : LocMemCache (utilisé en dev) est propre à chaque process. En prod,
# avec plusieurs workers, le compteur anti brute-force du login admin
# (apps/adminpanel/views.py) ne serait PAS partagé entre workers et la protection
# serait contournable. Redis n'étant pas disponible sur PythonAnywhere par défaut,
# on utilise un cache en base de données : plus lent que Redis, mais partagé entre
# workers et sans infrastructure supplémentaire. Nécessite une seule fois :
#   python manage.py createcachetable
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache_table",
    }
}