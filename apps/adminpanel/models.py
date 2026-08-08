from django.db import models


class AdminLog(models.Model):
    """Journal append-only des actions admin sensibles. Pas de FK vers
    `accounts.User` : l'admin n'est structurellement jamais un compte
    utilisateur classique dans cette architecture (voir apps.adminpanel
    services.verifier_identifiants). On garde seulement l'identifiant
    utilisé à la connexion."""

    admin_identifiant = models.CharField(max_length=150)
    action = models.CharField(max_length=100)  # ex. validation_annonce, suspension_compte
    cible = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Journal admin"
        verbose_name_plural = "Journal admin"

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} — {self.action} — {self.cible}"
