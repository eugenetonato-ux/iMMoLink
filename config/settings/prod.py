"""
Settings de production. À activer explicitement via
DJANGO_SETTINGS_MODULE=config.settings.prod (jamais par défaut).
"""
from decouple import config

from .base import *  # noqa: F401,F403

DEBUG = False

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
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# --- Cache partagé (Redis) ---
# Important : LocMemCache (utilisé en dev) est propre à chaque process. En prod,
# avec plusieurs workers Gunicorn, le compteur anti brute-force du login admin
# (apps/adminpanel/views.py) ne serait PAS partagé entre workers et la protection
# serait contournable. Redis est donc nécessaire ici, pas juste recommandé.
# Ajoute `redis` à requirements.txt et REDIS_URL dans ton .env de prod.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://127.0.0.1:6379/1"),
    }
}
