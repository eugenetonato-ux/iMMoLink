import secrets
import time

import pyotp
from django.conf import settings

from .models import AdminLog


def verifier_identifiants(username, password):
    """Compare aux identifiants définis dans `.env` (ADMIN_USERNAME/ADMIN_PASSWORD),
    jamais à la table `accounts.User`. Comparaison à temps constant pour éviter
    le timing attack le plus grossier."""
    if not settings.ADMIN_USERNAME or not settings.ADMIN_PASSWORD:
        return False
    ok_user = secrets.compare_digest(username or "", settings.ADMIN_USERNAME)
    ok_pass = secrets.compare_digest(password or "", settings.ADMIN_PASSWORD)
    return ok_user and ok_pass


def verifier_code_2fa(code):
    """Vérifie un code TOTP à 6 chiffres contre ADMIN_TOTP_SECRET (.env).
    Tolère une dérive d'horloge de +/- 30s (valid_window=1)."""
    if not settings.ADMIN_TOTP_SECRET or not code:
        return False
    totp = pyotp.TOTP(settings.ADMIN_TOTP_SECRET)
    return totp.verify(code.strip(), valid_window=1)


def demarrer_attente_2fa(request, username):
    """Ouvre la fenêtre d'attente du code 2FA après identifiants validés.
    Expire au bout de PENDING_2FA_TTL_SECONDS (voir vérification dans la vue)."""
    request.session["pending_admin_username"] = username
    request.session["pending_admin_2fa_since"] = time.time()


def attente_2fa_valide(request, ttl_seconds=300):
    """True si une attente 2FA est en cours et pas expirée (5 min par défaut)."""
    since = request.session.get("pending_admin_2fa_since")
    username = request.session.get("pending_admin_username")
    if not since or not username:
        return False
    return (time.time() - since) <= ttl_seconds


def nettoyer_attente_2fa(request):
    request.session.pop("pending_admin_username", None)
    request.session.pop("pending_admin_2fa_since", None)


def journaliser(request, action, cible=""):
    AdminLog.objects.create(
        admin_identifiant=request.session.get("admin_username", "admin"),
        action=action,
        cible=cible,
    )