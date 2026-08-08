import uuid

from django.conf import settings
from django.db import models


def generer_reference():
    return uuid.uuid4().hex


class Payment(models.Model):
    STATUT_CHOICES = [
        ("pending", "En attente"),
        ("successful", "Réussi"),
        ("failed", "Échoué"),
        ("cancelled", "Annulé"),
        ("refunded", "Remboursé"),
    ]
    METHODE_CHOICES = [
        ("moov_money", "Moov Money"),
        ("mtn_money", "MTN Money"),
    ]

    locataire = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="paiements"
    )
    annonce = models.ForeignKey("properties.Property", on_delete=models.PROTECT, related_name="paiements")
    proprietaire = models.ForeignKey(
        "accounts.OwnerProfile", on_delete=models.PROTECT, related_name="paiements_recus"
    )
    montant = models.DecimalField(max_digits=10, decimal_places=0)  # XOF
    reference = models.CharField(max_length=64, unique=True, default=generer_reference, editable=False)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="pending")
    methode = models.CharField(max_length=30, choices=METHODE_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"

    def __str__(self):
        return f"{self.reference} — {self.montant} XOF ({self.get_statut_display()})"


class ContactUnlock(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.PROTECT)
    locataire = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="contacts_debloques"
    )
    annonce = models.ForeignKey(
        "properties.Property", on_delete=models.CASCADE, related_name="contacts_debloques"
    )
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("locataire", "annonce")
        verbose_name = "Contact débloqué"
        verbose_name_plural = "Contacts débloqués"

    def __str__(self):
        return f"{self.locataire} → {self.annonce}"
