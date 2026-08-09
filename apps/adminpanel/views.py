import csv
from functools import wraps

from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.models import User
from apps.common.models import PlatformSettings
from apps.payments.models import Payment
from apps.properties.models import Property

from . import services
from .models import AdminLog


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def admin_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("is_admin"):
            return redirect("adminpanel:connexion")
        return view(request, *args, **kwargs)

    return wrapper


def connexion(request):
    if request.session.get("is_admin"):
        return redirect("adminpanel:dashboard")

    ip = _client_ip(request)

    if request.method == "POST":
        verrouille, _, retry_after = services.est_verrouille("login")

        if verrouille:
            minutes = max(1, retry_after // 60)
            messages.error(
                request,
                f"Trop de tentatives échouées. Réessayez dans {minutes} minute(s).",
            )
            return render(request, "Admin/connexion.html")

        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        if services.verifier_identifiants(username, password):
            services.enregistrer_tentative("login", ip, success=True)
            # Identifiants OK : on n'ouvre PAS encore la session admin,
            # on passe à l'étape 2FA.
            services.demarrer_attente_2fa(request, username)
            return redirect("adminpanel:verification_2fa")

        services.enregistrer_tentative("login", ip, success=False)
        _, tentatives_restantes, _ = services.est_verrouille("login")

        if tentatives_restantes == 0:
            messages.error(
                request,
                "Trop de tentatives échouées. Compte verrouillé pendant 15 minutes.",
            )
        else:
            messages.error(
                request,
                f"Identifiants incorrects. {tentatives_restantes} tentative(s) restante(s).",
            )

    return render(request, "Admin/connexion.html")


def verification_2fa(request):
    """Étape 2 : code TOTP. N'est accessible que si l'étape 1 vient de réussir
    (attente 2FA active et non expirée) — sinon retour au login."""
    if request.session.get("is_admin"):
        return redirect("adminpanel:dashboard")

    if not services.attente_2fa_valide(request):
        services.nettoyer_attente_2fa(request)
        messages.error(request, "Session expirée, veuillez vous reconnecter.")
        return redirect("adminpanel:connexion")

    ip = _client_ip(request)
    username = request.session.get("pending_admin_username")

    if request.method == "POST":
        verrouille, _, retry_after = services.est_verrouille("2fa")

        if verrouille:
            minutes = max(1, retry_after // 60)
            messages.error(
                request,
                f"Trop de tentatives échouées. Réessayez dans {minutes} minute(s).",
            )
            return render(request, "Admin/connexion_2fa.html")

        code = request.POST.get("code", "")

        if services.verifier_code_2fa(code):
            services.enregistrer_tentative("2fa", ip, success=True)
            services.nettoyer_attente_2fa(request)
            request.session["is_admin"] = True
            request.session["admin_username"] = username
            services.journaliser(request, "connexion_reussie")
            return redirect("adminpanel:dashboard")

        services.enregistrer_tentative("2fa", ip, success=False)
        _, tentatives_restantes, _ = services.est_verrouille("2fa")

        if tentatives_restantes == 0:
            services.nettoyer_attente_2fa(request)
            messages.error(
                request,
                "Trop de tentatives échouées. Compte verrouillé pendant 15 minutes.",
            )
            return redirect("adminpanel:connexion")
        else:
            messages.error(
                request,
                f"Code incorrect. {tentatives_restantes} tentative(s) restante(s).",
            )

    return render(request, "Admin/connexion_2fa.html")


@admin_required
def deconnexion(request):
    request.session.pop("is_admin", None)
    request.session.pop("admin_username", None)
    return redirect("adminpanel:connexion")


@admin_required
def dashboard(request):
    stats = {
        "utilisateurs_total": User.objects.count(),
        "locataires": User.objects.filter(role="locataire").count(),
        "proprietaires": User.objects.filter(role="proprietaire").count(),
        "annonces_publiees": Property.objects.filter(statut="publiee").count(),
        "annonces_en_attente": Property.objects.filter(statut="en_attente_validation").count(),
        "revenus_total": Payment.objects.filter(statut="successful").aggregate(total=Sum("montant"))["total"] or 0,
        "paiements_reussis": Payment.objects.filter(statut="successful").count(),
        "paiements_echoues": Payment.objects.filter(statut="failed").count(),
    }
    annonces_recentes = (
        Property.objects.filter(statut="en_attente_validation")
        .select_related("proprietaire__user")
        .order_by("-created_at")[:5]
    )
    return render(request, "Admin/dashboard.html", {"stats": stats, "annonces_recentes": annonces_recentes})


@admin_required
def annonces(request):
    statut = request.GET.get("statut", "en_attente_validation")
    queryset = Property.objects.select_related("proprietaire__user").order_by("-created_at")
    if statut:
        queryset = queryset.filter(statut=statut)
    return render(
        request,
        "Admin/annonces.html",
        {"annonces": queryset, "statut_filtre": statut, "statuts": Property.STATUT_CHOICES},
    )


@admin_required
def annonce_valider(request, pk):
    annonce = get_object_or_404(Property, pk=pk)
    annonce.statut = "publiee"
    annonce.publiee_le = timezone.now()
    annonce.save(update_fields=["statut", "publiee_le"])
    services.journaliser(request, "validation_annonce", str(annonce))
    messages.success(request, f"Annonce « {annonce.titre} » publiée.")
    return redirect("adminpanel:annonces")


@admin_required
def annonce_refuser(request, pk):
    annonce = get_object_or_404(Property, pk=pk)
    annonce.statut = "refusee"
    annonce.motif_refus = request.POST.get("motif", "")
    annonce.save(update_fields=["statut", "motif_refus"])
    services.journaliser(request, "refus_annonce", str(annonce))
    messages.warning(request, f"Annonce « {annonce.titre} » refusée.")
    return redirect("adminpanel:annonces")


@admin_required
def annonce_suspendre(request, pk):
    annonce = get_object_or_404(Property, pk=pk)
    annonce.statut = "suspendue"
    annonce.save(update_fields=["statut"])
    services.journaliser(request, "suspension_annonce", str(annonce))
    messages.warning(request, f"Annonce « {annonce.titre} » suspendue.")
    return redirect("adminpanel:annonces")


@admin_required
def utilisateurs(request):
    role = request.GET.get("role", "")
    queryset = User.objects.all().order_by("-date_joined")
    if role:
        queryset = queryset.filter(role=role)
    return render(request, "Admin/utilisateurs.html", {"utilisateurs": queryset, "role_filtre": role})


@admin_required
def utilisateur_suspendre(request, pk):
    utilisateur = get_object_or_404(User, pk=pk)
    utilisateur.is_active = False
    utilisateur.save(update_fields=["is_active"])
    services.journaliser(request, "suspension_compte", utilisateur.email)
    messages.warning(request, f"Compte {utilisateur.email} suspendu.")
    return redirect("adminpanel:utilisateurs")


@admin_required
def utilisateur_reactiver(request, pk):
    utilisateur = get_object_or_404(User, pk=pk)
    utilisateur.is_active = True
    utilisateur.save(update_fields=["is_active"])
    services.journaliser(request, "reactivation_compte", utilisateur.email)
    messages.success(request, f"Compte {utilisateur.email} réactivé.")
    return redirect("adminpanel:utilisateurs")


@admin_required
def transactions(request):
    queryset = Payment.objects.select_related("locataire", "annonce", "proprietaire__user").order_by("-created_at")
    return render(request, "Admin/transactions.html", {"transactions": queryset})


@admin_required
def transactions_export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="transactions_iMMoLink.csv"'
    writer = csv.writer(response)
    writer.writerow(["Référence", "Locataire", "Annonce", "Propriétaire", "Montant", "Méthode", "Statut", "Date"])
    for paiement in Payment.objects.select_related("locataire", "annonce", "proprietaire__user").order_by("-created_at"):
        writer.writerow(
            [
                paiement.reference,
                paiement.locataire.email,
                paiement.annonce.titre,
                paiement.proprietaire.user.email,
                paiement.montant,
                paiement.get_methode_display() if paiement.methode else "",
                paiement.get_statut_display(),
                paiement.created_at.strftime("%Y-%m-%d %H:%M"),
            ]
        )
    services.journaliser(request, "export_transactions_csv")
    return response


@admin_required
def parametres(request):
    config_obj = PlatformSettings.get_solo()
    if request.method == "POST":
        config_obj.frais_contact = request.POST.get("frais_contact") or config_obj.frais_contact
        config_obj.moov_money_actif = bool(request.POST.get("moov_money_actif"))
        config_obj.mtn_money_actif = bool(request.POST.get("mtn_money_actif"))
        config_obj.save()
        services.journaliser(request, "modification_parametres", f"frais_contact={config_obj.frais_contact}")
        messages.success(request, "Paramètres mis à jour.")
        return redirect("adminpanel:parametres")
    return render(request, "Admin/parametres.html", {"config": config_obj})


@admin_required
def logs(request):
    entries = AdminLog.objects.all()[:200]
    return render(request, "Admin/logs.html", {"logs": entries})