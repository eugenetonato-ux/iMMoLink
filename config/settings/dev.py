"""
Settings de développement local. Activé par défaut (voir manage.py / wsgi.py).
"""
from decouple import config

from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="127.0.0.1,localhost").split(",")

# En dev, les emails s'affichent dans la console au lieu d'être envoyés réellement
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Cache en mémoire locale — suffisant pour un seul process de dev
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
