from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("connexion/", views.connexion_view, name="connexion"),
    path("choix-role/", views.choix_role_view, name="choix_role"),
    path("deconnexion/", views.deconnexion_view, name="deconnexion"),
    path("completer-profil-proprietaire/", views.completer_profil_proprietaire, name="completer_profil_proprietaire"),
]