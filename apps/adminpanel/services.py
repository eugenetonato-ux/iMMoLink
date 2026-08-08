import secrets

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


def journaliser(request, action, cible=""):
    AdminLog.objects.create(
        admin_identifiant=request.session.get("admin_username", "admin"),
        action=action,
        cible=cible,
    )
