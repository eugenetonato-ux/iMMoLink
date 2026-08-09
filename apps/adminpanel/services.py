import secrets
import time

import pyotp
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import AdminLog, AdminLoginAttempt

# --- Anti-brute-force GLOBAL et PERSISTANT (remplace le cache) ---
# Global : le compteur ne dépend pas de l'IP, donc changer d'IP entre
# chaque essai ne permet pas de contourner le blocage.
# Persistant : basé sur la base de données, donc survit aux redémarrages
# fréquents du serveur (contrairement à un compteur en cache mémoire).
MAX_ATTEMPTS = 5
LOCKOUT_WINDOW_MINUTES = 15  # fenêtre glissante d'observation
LOCKOUT_DURATION_MINUTES = 15  # durée du blocage une fois le seuil atteint


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


def est_verrouille(etape):
    """Vérifie si l'étape donnée ('login' ou '2fa') est actuellement
    verrouillée, tous IP confondus. Retourne (verrouille: bool,
    tentatives_restantes: int, retry_after_seconds: int)."""
    fenetre_debut = timezone.now() - timedelta(minutes=LOCKOUT_WINDOW_MINUTES)

    echecs_recents = AdminLoginAttempt.objects.filter(
        etape=etape, success=False, created_at__gte=fenetre_debut
    ).order_by("-created_at")

    nb_echecs = echecs_recents.count()

    if nb_echecs < MAX_ATTEMPTS:
        return False, max(MAX_ATTEMPTS - nb_echecs, 0), 0

    # Seuil atteint : verrouillé jusqu'à LOCKOUT_DURATION_MINUTES après
    # le dernier échec comptabilisé (la vue ne comptabilise plus de
    # nouvel échec tant que le blocage est actif, donc la durée reste fixe)
    dernier_echec = echecs_recents.first()
    deverrouillage = dernier_echec.created_at + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
    retry_after = max(0, int((deverrouillage - timezone.now()).total_seconds()))

    if retry_after == 0:
        return False, 0, 0

    return True, 0, retry_after


def enregistrer_tentative(etape, ip_address, success):
    AdminLoginAttempt.objects.create(etape=etape, ip_address=ip_address, success=success)
    if success:
        # Connexion réussie : on efface l'historique d'échecs de cette
        # étape pour repartir sur une base propre.
        AdminLoginAttempt.objects.filter(etape=etape, success=False).delete()


def journaliser(request, action, cible=""):
    AdminLog.objects.create(
        admin_identifiant=request.session.get("admin_username", "admin"),
        action=action,
        cible=cible,
    )