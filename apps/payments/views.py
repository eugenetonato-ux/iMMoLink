import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.properties.models import Property

from . import services
from .models import Payment

logger = logging.getLogger(__name__)


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
@require_POST
def lancer_paiement(request, reference):
    """Envoie la demande de paiement à Sebpay (push sur le téléphone du
    locataire). Utilisé en production, quand une vraie clé Sebpay est
    configurée."""
    paiement = get_object_or_404(Payment, reference=reference, locataire=request.user)

    telephone = request.POST.get("telephone", "").strip().lstrip("+")
    methode = request.POST.get("methode", "")

    if not telephone or not telephone.isdigit() or len(telephone) < 8:
        messages.error(request, "Merci de renseigner un numéro Mobile Money valide.")
        return redirect("payments:initier", annonce_id=paiement.annonce_id)

    try:
        services.lancer_paiement_sebpay(paiement, telephone=telephone, methode=methode)
    except ValueError:
        messages.error(request, "Merci de choisir un moyen de paiement valide.")
        return redirect("payments:initier", annonce_id=paiement.annonce_id)
    except services.SebpayError:
        messages.error(request, "Impossible de contacter Sebpay pour le moment, réessaie dans un instant.")
        return redirect("payments:initier", annonce_id=paiement.annonce_id)

    messages.info(request, "Vérifie ton téléphone pour valider le paiement.")
    return render(request, "Website/paiement_attente.html", {"paiement": paiement, "annonce": paiement.annonce})


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


@login_required
def statut_paiement(request, reference):
    """Interrogée en JS (polling) par paiement_attente.html pour savoir si
    le webhook Sebpay a déjà confirmé le paiement."""
    paiement = get_object_or_404(Payment, reference=reference, locataire=request.user)
    return JsonResponse({"statut": paiement.statut})


def _verifier_signature_sebpay(request):
    """Vérifie l'en-tête X-SebPay-Signature (HMAC-SHA256 du body, calculé
    avec la clé secrète sk_live_...)."""
    signature_recue = request.headers.get(settings.SEBPAY_SIGNATURE_HEADER, "")
    if not signature_recue:
        return False

    signature_calculee = hmac.new(
        settings.SEBPAY_SECRET_KEY.encode("utf-8"),
        request.body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(signature_recue, signature_calculee)


@csrf_exempt
@require_POST
def webhook_sebpay(request):
    """Reçoit la confirmation de paiement envoyée par Sebpay (statut final :
    'approved' ou 'rejected')."""
    if not _verifier_signature_sebpay(request):
        logger.warning("Webhook Sebpay reçu avec une signature invalide ou absente.")
        return HttpResponse(status=403)

    try:
        data = json.loads(request.body)
    except (ValueError, TypeError):
        return HttpResponse(status=400)

    reference = data.get("external_reference")
    statut = data.get("status")

    if not reference:
        return HttpResponse(status=400)

    try:
        paiement = Payment.objects.get(reference=reference)
    except Payment.DoesNotExist:
        logger.warning("Webhook Sebpay reçu pour une référence inconnue : %s", reference)
        return HttpResponse(status=404)

    if statut == "approved":
        services.confirmer_paiement(paiement)
    elif statut == "rejected":
        services.echouer_paiement(paiement)

    return HttpResponse(status=200)