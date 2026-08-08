from django.urls import path

from . import views

app_name = "adminpanel"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("connexion/", views.connexion, name="connexion"),
    path("deconnexion/", views.deconnexion, name="deconnexion"),
    path("annonces/", views.annonces, name="annonces"),
    path("annonces/<int:pk>/valider/", views.annonce_valider, name="annonce_valider"),
    path("annonces/<int:pk>/refuser/", views.annonce_refuser, name="annonce_refuser"),
    path("annonces/<int:pk>/suspendre/", views.annonce_suspendre, name="annonce_suspendre"),
    path("utilisateurs/", views.utilisateurs, name="utilisateurs"),
    path("utilisateurs/<int:pk>/suspendre/", views.utilisateur_suspendre, name="utilisateur_suspendre"),
    path("utilisateurs/<int:pk>/reactiver/", views.utilisateur_reactiver, name="utilisateur_reactiver"),
    path("transactions/", views.transactions, name="transactions"),
    path("transactions/export/", views.transactions_export_csv, name="transactions_export"),
    path("parametres/", views.parametres, name="parametres"),
    path("logs/", views.logs, name="logs"),
]
