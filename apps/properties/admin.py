from django.contrib import admin

from .models import Amenity, Property, PropertyAmenity, PropertyImage


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


class PropertyAmenityInline(admin.TabularInline):
    # `amenities` a un through model explicite (PropertyAmenity) : il faut donc
    # passer par un inline plutôt que par filter_horizontal pour l'éditer.
    model = PropertyAmenity
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("titre", "proprietaire", "commune", "quartier", "prix", "statut", "disponibilite", "created_at")
    list_filter = ("statut", "type_logement", "commune", "disponibilite")
    search_fields = ("titre", "commune__nom", "quartier__nom", "proprietaire__user__email")
    inlines = [PropertyImageInline, PropertyAmenityInline]


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ("nom", "icone")