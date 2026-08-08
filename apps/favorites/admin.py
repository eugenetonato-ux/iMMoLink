from django.contrib import admin

from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("locataire", "annonce", "created_at")
    search_fields = ("locataire__email", "annonce__titre")
