from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("initier/<int:annonce_id>/", views.initier_paiement, name="initier"),
    path("confirmer-dev/<str:reference>/", views.confirmer_paiement_dev, name="confirmer_dev"),
    path("annuler/<str:reference>/", views.annuler_paiement, name="annuler"),
]
