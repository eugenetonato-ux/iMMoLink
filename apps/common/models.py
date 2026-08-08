from decouple import config as env_config
from django.db import models


class PlatformSettings(models.Model):
    """Configuration globale de la plateforme, modifiable uniquement depuis
    l'espace admin (`cpanel_administrateur`). Table singleton : une seule ligne
    (pk=1). Le montant des frais de mise en relation ne doit jamais être codé
    en dur ailleurs dans le code — toujours lu via `PlatformSettings.get_solo()`.
    """

    frais_contact = models.DecimalField(
        max_digits=10, decimal_places=0, default=1000,
        help_text="Frais de mise en relation locataire → propriétaire, en XOF.",
    )
    devise = models.CharField(max_length=10, default="XOF")
    moov_money_actif = models.BooleanField(default=True)
    mtn_money_actif = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Paramètres plateforme"
        verbose_name_plural = "Paramètres plateforme"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Singleton : jamais supprimable.
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                "frais_contact": env_config("DEFAULT_CONTACT_FEE", default=1000, cast=int),
                "devise": env_config("CURRENCY", default="XOF"),
            },
        )
        return obj

    def __str__(self):
        return f"Paramètres de la plateforme (frais de contact : {self.frais_contact} {self.devise})"
