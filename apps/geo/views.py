from django.http import JsonResponse

from .models import Commune, Arrondissement, Locality


def communes_by_department(request):
    """Retourne les communes d'un département donné."""
    department_id = request.GET.get("department_id")

    if not department_id:
        return JsonResponse({"results": []})

    communes = Commune.objects.filter(
        department_id=department_id
    ).order_by("nom")

    data = [
        {
            "id": commune.id,
            "nom": commune.nom,
        }
        for commune in communes
    ]

    return JsonResponse({"results": data})


def arrondissements_by_commune(request):
    """Retourne les arrondissements d'une commune donnée."""
    commune_id = request.GET.get("commune_id")

    if not commune_id:
        return JsonResponse({"results": []})

    arrondissements = Arrondissement.objects.filter(
        commune_id=commune_id
    ).order_by("nom")

    data = [
        {
            "id": arrondissement.id,
            "nom": arrondissement.nom,
        }
        for arrondissement in arrondissements
    ]

    return JsonResponse({"results": data})


def localities_by_arrondissement(request):
    """Retourne les quartiers/villages d'un arrondissement donné."""
    arrondissement_id = request.GET.get("arrondissement_id")

    if not arrondissement_id:
        return JsonResponse({"results": []})

    localities = Locality.objects.filter(
        arrondissement_id=arrondissement_id
    ).order_by("nom")

    data = [
        {
            "id": locality.id,
            "nom": locality.nom,
            "type": locality.locality_type,
        }
        for locality in localities
    ]

    return JsonResponse({"results": data})