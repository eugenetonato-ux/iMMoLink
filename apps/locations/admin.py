from django.contrib import admin

from .models import Quartier, Ville


class QuartierInline(admin.TabularInline):
    model = Quartier
    extra = 1


@admin.register(Ville)
class VilleAdmin(admin.ModelAdmin):
    list_display = ("nom", "slug", "est_populaire", "ordre")
    list_filter = ("est_populaire",)
    prepopulated_fields = {"slug": ("nom",)}
    inlines = [QuartierInline]


@admin.register(Quartier)
class QuartierAdmin(admin.ModelAdmin):
    list_display = ("nom", "ville")
    list_filter = ("ville",)
    search_fields = ("nom",)
