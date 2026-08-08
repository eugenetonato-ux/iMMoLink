from django.db import transaction
from django.utils import timezone

from apps.common.models import PlatformSettings

from .models import ContactUnlock, Payment


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


@transaction.atomic
def confirmer_paiement(payment, methode=""):
    """Confirme un paiement réussi et débloque le contact — traitement
    idempotent (pas de double déblocage/double log même si appelé plusieurs
    fois pour la même référence, ce que fait un vrai webhook signé Sebpay
    en cas de retry réseau)."""
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
        return  # déjà confirmé, on ne régresse jamais un paiement réussi
    payment.statut = "failed"
    payment.save(update_fields=["statut"])
