from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.properties.models import Property

from . import services
from .models import Payment


@login_required
def initier_paiement(request, annonce_id):
    annonce = get_object_or_404(Property, pk=annonce_id, statut="publiee")

    if request.user.role != "locataire":
        messages.info(request, "Connecte-toi en tant que locataire pour contacter un propriétaire.")
        return redirect("accounts:choix_role")

    paiement = services.initier_paiement(request.user, annonce)
    if paiement.statut == "successful":
        return redirect("website:annonce_detail", pk=annonce.pk)

    return render(
        request,
        "Website/paiement.html",
        {"annonce": annonce, "paiement": paiement, "debug": settings.DEBUG},
    )


@login_required
def confirmer_paiement_dev(request, reference):
    """Confirmation simulée réservée au développement local (aucune clé
    Sebpay n'est configurée dans `.env`). En production, cette vue est
    remplacée par le webhook Sebpay signé qui appelle
    `apps.payments.services.confirmer_paiement` — jamais une action côté
    client, et jamais sur un statut autre que la confirmation réelle du
    prestataire de paiement."""
    if not settings.DEBUG:
        messages.error(request, "Confirmation indisponible.")
        return redirect("website:home")

    paiement = get_object_or_404(Payment, reference=reference, locataire=request.user)
    if request.method == "POST":
        methode = request.POST.get("methode", "moov_money")
        services.confirmer_paiement(paiement, methode=methode)
        messages.success(request, "Paiement confirmé — le contact est débloqué.")
        return redirect("website:annonce_detail", pk=paiement.annonce.pk)
    return redirect("payments:initier", annonce_id=paiement.annonce_id)


@login_required
def annuler_paiement(request, reference):
    paiement = get_object_or_404(Payment, reference=reference, locataire=request.user)
    services.echouer_paiement(paiement)
    messages.warning(request, "Paiement annulé.")
    return redirect("website:annonce_detail", pk=paiement.annonce.pk)
