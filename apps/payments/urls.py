from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("initier/<int:annonce_id>/", views.initier_paiement, name="initier"),
    path("lancer/<str:reference>/", views.lancer_paiement, name="lancer"),
    path("statut/<str:reference>/", views.statut_paiement, name="statut"),
    path("confirmer-dev/<str:reference>/", views.confirmer_paiement_dev, name="confirmer_dev"),
    path("annuler/<str:reference>/", views.annuler_paiement, name="annuler"),
    path("webhook/sebpay/", views.webhook_sebpay, name="webhook_sebpay"),
]