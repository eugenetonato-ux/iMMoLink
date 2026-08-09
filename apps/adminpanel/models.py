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


class AdminLoginAttempt(models.Model):
    """Trace chaque tentative de connexion admin (étape mot de passe OU
    étape 2FA), pour un anti-brute-force GLOBAL (pas par IP — une seule
    IP différente à chaque essai ne permet pas de contourner le blocage)
    et PERSISTANT en base (survit aux redémarrages fréquents du serveur,
    contrairement à un compteur en cache mémoire)."""

    ETAPE_CHOICES = [
        ("login", "Mot de passe"),
        ("2fa", "Code 2FA"),
    ]

    etape = models.CharField(max_length=10, choices=ETAPE_CHOICES)
    ip_address = models.GenericIPAddressField()
    success = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        status = "OK" if self.success else "ÉCHEC"
        return f"[{status}] {self.get_etape_display()} @ {self.ip_address} ({self.created_at:%Y-%m-%d %H:%M})"