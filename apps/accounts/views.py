from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from . import services
from .models import OwnerProfile


def connexion_view(request):
    """Page d'accueil de connexion — bouton 'Se connecter avec Google'."""
    if request.user.is_authenticated:
        return redirect("accounts:choix_role")
    return render(request, "Website/connexion.html")


@login_required
def choix_role_view(request):
    """Redirige vers le bon espace si le rôle est déjà défini,
    sinon affiche le choix locataire/propriétaire."""
    if request.user.role == "proprietaire":
        return redirect("owner:owner_dashboard")
    if request.user.role == "locataire":
        return redirect("tenant:tenant_dashboard")

    if request.method == "POST":
        role = request.POST.get("role")
        try:
            services.attribuer_role(request.user, role)
        except ValueError:
            messages.error(request, "Rôle invalide.")
            return redirect("accounts:choix_role")
        return redirect("accounts:choix_role")

    return render(request, "Website/choix_role.html")


@login_required
def deconnexion_view(request):
    logout(request)
    return redirect("website:home")


@login_required
def tenant_dashboard(request):
    if request.user.role != "locataire":
        return redirect("accounts:choix_role")

    from apps.favorites.models import Favorite
    from apps.payments.models import ContactUnlock, Payment

    stats = {
        "favoris": Favorite.objects.filter(locataire=request.user).count(),
        "contacts_debloques": ContactUnlock.objects.filter(locataire=request.user).count(),
        "paiements": Payment.objects.filter(locataire=request.user).count(),
    }
    derniers_contacts = (
        ContactUnlock.objects.filter(locataire=request.user)
        .select_related("annonce")
        .order_by("-unlocked_at")[:5]
    )
    return render(
        request,
        "Tenant/dashboard.html",
        {"stats": stats, "derniers_contacts": derniers_contacts},
    )


@login_required
def owner_dashboard(request):
    if request.user.role != "proprietaire":
        return redirect("accounts:choix_role")
    if not services.profil_proprietaire_complet(request.user):
        return redirect("accounts:completer_profil_proprietaire")

    from apps.properties.models import Property

    profil = request.user.ownerprofile
    annonces = Property.objects.filter(proprietaire=profil)
    stats = {
        "total": annonces.count(),
        "publiees": annonces.filter(statut="publiee").count(),
        "en_attente": annonces.filter(statut="en_attente_validation").count(),
        "refusees": annonces.filter(statut="refusee").count(),
    }
    dernieres_annonces = annonces.order_by("-created_at")[:5]
    return render(
        request,
        "Owner/dashboard.html",
        {"stats": stats, "dernieres_annonces": dernieres_annonces},
    )


@login_required
def completer_profil_proprietaire(request):
    if request.user.role != "proprietaire":
        return redirect("accounts:choix_role")

    profil = OwnerProfile.objects.filter(user=request.user).first()

    if request.method == "POST":
        services.creer_ou_maj_profil_proprietaire(
            request.user,
            whatsapp=request.POST.get("whatsapp"),
            ville=request.POST.get("ville"),
            quartier=request.POST.get("quartier"),
            adresse=request.POST.get("adresse", ""),
            photo_profil=request.FILES.get("photo_profil"),
        )
        if services.profil_proprietaire_complet(request.user):
            messages.success(request, "Profil complété — tu peux publier une annonce.")
            return redirect("owner:owner_dashboard")
        messages.error(request, "Merci de compléter tous les champs obligatoires, y compris la photo de profil.")

    from apps.locations.models import Ville

    return render(
        request,
        "Owner/completer_profil.html",
        {"profil": profil, "villes": Ville.objects.all()},
    )