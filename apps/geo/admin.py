from django.contrib import admin

from .models import Arrondissement, Commune, Department, Locality


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("nom",)
    search_fields = ("nom",)


@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    list_display = ("nom", "department")
    list_filter = ("department",)
    search_fields = ("nom",)


@admin.register(Arrondissement)
class ArrondissementAdmin(admin.ModelAdmin):
    list_display = ("nom", "commune")
    list_filter = ("commune__department", "commune")
    search_fields = ("nom",)


@admin.register(Locality)
class LocalityAdmin(admin.ModelAdmin):
    list_display = ("nom", "locality_type", "arrondissement")
    list_filter = ("locality_type", "arrondissement__commune__department")
    search_fields = ("nom",)