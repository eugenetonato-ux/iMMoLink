from django.http import JsonResponse

from .models import Quartier


def quartiers_par_ville(request, ville_id):
    """Utilisé par le formulaire de création d'annonce (JS) pour peupler
    dynamiquement la liste des quartiers une fois la ville choisie."""
    quartiers = list(Quartier.objects.filter(ville_id=ville_id).values("id", "nom"))
    return JsonResponse({"quartiers": quartiers})
