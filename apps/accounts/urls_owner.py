from django.urls import path

from apps.properties import views as property_views

from . import views

app_name = "owner"

urlpatterns = [
    path("", views.owner_dashboard, name="owner_dashboard"),
    path("annonces/", property_views.mes_annonces, name="mes_annonces"),
    path("annonces/nouvelle/", property_views.annonce_form, name="annonce_nouvelle"),
    path("annonces/<int:pk>/modifier/", property_views.annonce_form, name="annonce_modifier"),
    path("annonces/<int:pk>/valider/", property_views.annonce_envoyer_validation, name="annonce_envoyer_validation"),
    path("annonces/<int:pk>/retirer/", property_views.annonce_retirer, name="annonce_retirer"),
    path("annonces/<int:pk>/supprimer/", property_views.annonce_supprimer, name="annonce_supprimer"),
]