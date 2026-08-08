def platform(request):
    """Rend `favoris_count` disponible dans tous les templates du site public
    (badge du header) sans que chaque vue ait à le calculer explicitement."""
    favoris_count = 0
    user = getattr(request, "user", None)
    if user and user.is_authenticated and getattr(user, "role", "") == "locataire":
        from apps.favorites.models import Favorite

        favoris_count = Favorite.objects.filter(locataire=user).count()
    return {"favoris_count": favoris_count}
