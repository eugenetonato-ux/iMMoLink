from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.services import profil_proprietaire_complet
from apps.locations.models import Ville

from . import services
from .models import Amenity, Property


@login_required
def mes_annonces(request):
    if request.user.role != "proprietaire":
        return redirect("accounts:choix_role")
    if not profil_proprietaire_complet(request.user):
        messages.info(request, "Complète d'abord ton profil propriétaire.")
        return redirect("accounts:completer_profil_proprietaire")
    profil = request.user.ownerprofile
    annonces = Property.objects.filter(proprietaire=profil).order_by("-created_at")
    return render(request, "Owner/annonces.html", {"annonces": annonces})


@login_required
def annonce_form(request, pk=None):
    if request.user.role != "proprietaire":
        return redirect("accounts:choix_role")
    if not profil_proprietaire_complet(request.user):
        messages.info(request, "Complète d'abord ton profil propriétaire avant de publier une annonce.")
        return redirect("accounts:completer_profil_proprietaire")

    profil = request.user.ownerprofile
    annonce = get_object_or_404(Property, pk=pk, proprietaire=profil) if pk else None

    if annonce and annonce.statut not in ("brouillon", "refusee"):
        messages.info(request, "Cette annonce ne peut plus être modifiée directement (déjà en validation ou publiée).")
        return redirect("owner:mes_annonces")

    if request.method == "POST":
        annonce = services.enregistrer_annonce(profil, annonce, request.POST, request.FILES)
        if request.POST.get("action") == "envoyer_validation":
            services.soumettre_pour_validation(annonce)
            messages.success(request, "Annonce envoyée pour validation à l'équipe iMMoLink.")
        else:
            messages.success(request, "Brouillon enregistré.")
        return redirect("owner:mes_annonces")

    return render(
        request,
        "Owner/annonce_form.html",
        {
            "annonce": annonce,
            "amenities": Amenity.objects.all(),
            "villes": Ville.objects.all(),
            "amenity_ids_selectionnes": set(annonce.amenities.values_list("id", flat=True)) if annonce else set(),
        },
    )


@login_required
@require_POST
def annonce_envoyer_validation(request, pk):
    if request.user.role != "proprietaire":
        return redirect("accounts:choix_role")
    if not profil_proprietaire_complet(request.user):
        return redirect("accounts:completer_profil_proprietaire")
    profil = request.user.ownerprofile
    annonce = get_object_or_404(Property, pk=pk, proprietaire=profil)
    services.soumettre_pour_validation(annonce)
    messages.success(request, "Annonce envoyée pour validation.")
    return redirect("owner:mes_annonces")


@login_required
@require_POST
def annonce_supprimer(request, pk):
    if request.user.role != "proprietaire":
        return redirect("accounts:choix_role")
    if not profil_proprietaire_complet(request.user):
        return redirect("accounts:completer_profil_proprietaire")
    profil = request.user.ownerprofile
    annonce = get_object_or_404(Property, pk=pk, proprietaire=profil)
    if annonce.statut in ("brouillon", "refusee"):
        annonce.delete()
        messages.success(request, "Annonce supprimée.")
    else:
        messages.error(request, "Impossible de supprimer une annonce publiée ou en cours de validation.")
    return redirect("owner:mes_annonces")
