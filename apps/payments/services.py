import logging

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.common.models import PlatformSettings

from .models import ContactUnlock, Payment

logger = logging.getLogger(__name__)


def initier_paiement(locataire, annonce, methode=""):
    """Crée (ou réutilise) une transaction en attente pour débloquer le
    contact d'une annonce. Le montant est toujours lu depuis la configuration
    plateforme (`PlatformSettings`), jamais codé en dur."""
    unlock_existant = ContactUnlock.objects.filter(locataire=locataire, annonce=annonce).first()
    if unlock_existant:
        return unlock_existant.payment

    paiement_en_attente = Payment.objects.filter(
        locataire=locataire, annonce=annonce, statut="pending"
    ).first()
    if paiement_en_attente:
        return paiement_en_attente

    frais = PlatformSettings.get_solo().frais_contact
    return Payment.objects.create(
        locataire=locataire,
        annonce=annonce,
        proprietaire=annonce.proprietaire,
        montant=frais,
        methode=methode,
    )


class SebpayError(Exception):
    """Levée quand l'appel à l'API Sebpay échoue ou renvoie une erreur."""


def _appeler_api_sebpay(payment, telephone, methode):
    """Envoie la demande de collecte à Sebpay."""
    operator_slug = {"moov_money": "moov", "mtn_money": "mtn"}.get(methode, methode)

    payload = {
        "amount": int(payment.montant),
        "currency": "XOF",
        "phone": telephone,
        "operator": operator_slug,
        "country": "BJ",
        "external_reference": payment.reference,
        "callback_url": settings.SEBPAY_WEBHOOK_URL,
    }
    headers = {
        "Authorization": f"Bearer {settings.SEBPAY_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        reponse = requests.post(
            settings.SEBPAY_API_URL,
            json=payload,
            headers=headers,
            timeout=15,
        )
        reponse.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Échec appel Sebpay pour %s : %s", payment.reference, exc)
        raise SebpayError(str(exc)) from exc

    return reponse.json()


def lancer_paiement_sebpay(payment, telephone, methode):
    """Envoie la demande à Sebpay et enregistre le numéro/la méthode choisis.
    Ne débloque rien : la confirmation réelle vient uniquement du webhook."""
    if methode not in dict(Payment.METHODE_CHOICES):
        raise ValueError(f"Méthode de paiement invalide : {methode}")

    data = _appeler_api_sebpay(payment, telephone, methode)

    payment.telephone = telephone
    payment.methode = methode
    payment.sebpay_transaction_id = data.get("transaction_id", "")
    payment.save(update_fields=["telephone", "methode", "sebpay_transaction_id"])
    return payment


@transaction.atomic
def confirmer_paiement(payment, methode=""):
    """Confirme un paiement réussi et débloque le contact — traitement
    idempotent (pas de double déblocage/double log même si appelé plusieurs
    fois pour la même référence, ce que fait un vrai webhook signé Sebpay
    en cas de retry réseau)."""
    if methode and methode not in dict(Payment.METHODE_CHOICES):
        raise ValueError(f"Méthode de paiement invalide : {methode}")

    payment = Payment.objects.select_for_update().get(pk=payment.pk)

    if payment.statut == "successful":
        return ContactUnlock.objects.filter(payment=payment).first()

    payment.statut = "successful"
    payment.confirmed_at = timezone.now()
    if methode:
        payment.methode = methode
    payment.save(update_fields=["statut", "confirmed_at", "methode"])

    unlock, _ = ContactUnlock.objects.get_or_create(
        payment=payment,
        defaults={"locataire": payment.locataire, "annonce": payment.annonce},
    )
    return unlock


def echouer_paiement(payment):
    if payment.statut == "successful":
        return
    payment.statut = "failed"
    payment.save(update_fields=["statut"])