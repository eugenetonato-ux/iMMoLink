# apps/geo/urls.py (nouveau fichier)
from django.urls import path
from . import views

app_name = "geo"

urlpatterns = [
    path("communes/", views.communes_by_department, name="communes_by_department"),
    path("arrondissements/", views.arrondissements_by_commune, name="arrondissements_by_commune"),
    path("localities/", views.localities_by_arrondissement, name="localities_by_arrondissement"),
]