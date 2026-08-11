from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.common.models import PlatformSettings
from apps.geo.models import Commune, Department
from apps.properties.models import Property


def _communes_avec_compteur():
    """Annote chaque commune avec son nombre d'annonces publiées (petit
    référentiel — quelques dizaines de communes au plus, pas besoin d'une
    requête corrélée complexe)."""
    communes = list(Commune.objects.all())
    for commune in communes:
        commune.nb_annonces = Property.objects.filter(statut="publiee", commune=commune).count()
    return communes


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
    communes = _communes_avec_compteur()
    communes_populaires = sorted(
        [c for c in communes if c.nb_annonces > 0],
        key=lambda c: -c.nb_annonces,
    )[:6]
    return render(
        request,
        "Website/home.html",
        {
            "annonces": annonces,
            "communes_populaires": communes_populaires,
            "favoris_ids": _favoris_ids(request.user),
            "departments": Department.objects.all(),
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
    commune_id = request.GET.get("commune", "").strip()
    quartier_id = request.GET.get("quartier", "").strip()
    type_logement = request.GET.get("type")
    prix_min = request.GET.get("prix_min")
    prix_max = request.GET.get("prix_max")
    chambres = request.GET.get("chambres")

    # Recherche libre : on matche sur le nom de la commune ou du quartier.
    if q:
        annonces = annonces.filter(Q(commune__nom__icontains=q) | Q(quartier__nom__icontains=q))
    if commune_id:
        annonces = annonces.filter(commune_id=commune_id)
    if quartier_id:
        annonces = annonces.filter(quartier_id=quartier_id)
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

    commune_selectionnee = Commune.objects.filter(pk=commune_id).first() if commune_id else None

    return render(
        request,
        "Website/recherche.html",
        {
            "annonces": page_obj,
            "departments": Department.objects.all(),
            "commune_selectionnee": commune_selectionnee,
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