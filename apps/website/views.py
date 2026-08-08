from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.common.models import PlatformSettings
from apps.locations.models import Ville
from apps.properties.models import Property


def _villes_avec_compteur():
    """Annote chaque ville avec son nombre d'annonces publiées (petit
    référentiel — quelques dizaines de villes au plus, pas besoin d'une
    requête corrélée complexe)."""
    villes = list(Ville.objects.all())
    for ville in villes:
        ville.nb_annonces = Property.objects.filter(statut="publiee", ville__iexact=ville.nom).count()
    return villes


def _favoris_ids(user):
    """IDs des annonces déjà en favori pour le locataire connecté — utilisé
    pour que le cœur ❤️ des cartes reflète le bon état dès le chargement de
    la page, au lieu de toujours démarrer vide (état visuel désynchronisé
    tant qu'on ne clique pas dessus)."""
    if not user.is_authenticated or user.role != "locataire":
        return set()
    from apps.favorites.models import Favorite

    return set(Favorite.objects.filter(locataire=user).values_list("annonce_id", flat=True))


def home(request):
    annonces = Property.objects.filter(statut="publiee").order_by("-created_at")[:8]
    villes = _villes_avec_compteur()
    villes_populaires = sorted(
        [v for v in villes if v.est_populaire or v.nb_annonces > 0],
        key=lambda v: (-v.nb_annonces, v.ordre),
    )[:6]
    return render(
        request,
        "Website/home.html",
        {
            "annonces": annonces,
            "villes": villes,
            "villes_populaires": villes_populaires,
            "favoris_ids": _favoris_ids(request.user),
        },
    )


def apropos(request):
    from django.contrib.auth import get_user_model
    from apps.payments.models import ContactUnlock

    User = get_user_model()

    context = {
        "nb_logements": Property.objects.filter(statut="publiee").count(),
        "nb_utilisateurs": User.objects.filter(role__in=["locataire", "proprietaire"]).count(),
        "nb_mises_en_relation": ContactUnlock.objects.count(),
    }
    return render(request, "Website/apropos.html", context)


def recherche(request):
    annonces = Property.objects.filter(statut="publiee")

    q = request.GET.get("q", "").strip()
    ville = request.GET.get("ville", "").strip()
    quartier = request.GET.get("quartier", "").strip()
    type_logement = request.GET.get("type")
    prix_min = request.GET.get("prix_min")
    prix_max = request.GET.get("prix_max")
    chambres = request.GET.get("chambres")

    # Le locataire écrit librement la ville/le quartier voulu (pas de liste
    # imposée) : on filtre par correspondance partielle, insensible à la casse.
    if q:
        annonces = annonces.filter(Q(ville__icontains=q) | Q(quartier__icontains=q))
    if ville:
        annonces = annonces.filter(ville__icontains=ville)
    if quartier:
        annonces = annonces.filter(quartier__icontains=quartier)
    if type_logement:
        annonces = annonces.filter(type_logement=type_logement)
    if prix_min:
        annonces = annonces.filter(prix__gte=prix_min)
    if prix_max:
        annonces = annonces.filter(prix__lte=prix_max)
    if chambres:
        annonces = annonces.filter(chambres__gte=chambres)

    annonces = annonces.order_by("-created_at")

    paginator = Paginator(annonces, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "Website/recherche.html",
        {
            "annonces": page_obj,
            "villes": Ville.objects.all(),
            "ville_selectionnee": ville or None,
            "favoris_ids": _favoris_ids(request.user),
        },
    )


def annonce_detail(request, pk):
    annonce = get_object_or_404(Property, pk=pk, statut="publiee")

    contact_debloque = False
    whatsapp_link = None

    if request.user.is_authenticated:
        from apps.payments.models import ContactUnlock

        unlock = ContactUnlock.objects.filter(locataire=request.user, annonce=annonce).first()
        if unlock:
            contact_debloque = True
            whatsapp_link = f"https://wa.me/{annonce.proprietaire.whatsapp}"

    return render(
        request,
        "Website/annonce_detail.html",
        {
            "annonce": annonce,
            "contact_debloque": contact_debloque,
            "whatsapp_link": whatsapp_link,
            "frais_contact": PlatformSettings.get_solo().frais_contact,
        },
    )


@login_required
def annonce_contact(request, pk):
    """Point d'entrée vers le paiement des frais de mise en relation (app payments)."""
    annonce = get_object_or_404(Property, pk=pk, statut="publiee")

    if request.user.role != "locataire":
        messages.info(request, "Connecte-toi en tant que locataire pour contacter un propriétaire.")
        return redirect("accounts:choix_role")

    return redirect("payments:initier", annonce_id=annonce.pk)