from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from apps.properties.models import Property

from .models import Favorite


@login_required
@require_POST
def toggle_favorite(request, annonce_id):
    annonce = get_object_or_404(Property, pk=annonce_id)
    favori, created = Favorite.objects.get_or_create(locataire=request.user, annonce=annonce)
    if not created:
        favori.delete()
        etat = False
    else:
        etat = True
    total = Favorite.objects.filter(locataire=request.user).count()
    return JsonResponse({"favori": etat, "total": total})


@login_required
def mes_favoris(request):
    annonces = list(
        Property.objects.filter(favoris__locataire=request.user, statut="publiee")
        .order_by("-favoris__created_at")
    )
    # Toutes les annonces de cette page sont par définition des favoris : le
    # cœur ❤️ de chaque carte doit démarrer plein (même composant partagé
    # que la recherche/l'accueil, qui utilise ce même indicateur).
    favoris_ids = {annonce.pk for annonce in annonces}
    return render(request, "Tenant/favoris.html", {"annonces": annonces, "favoris_ids": favoris_ids})
