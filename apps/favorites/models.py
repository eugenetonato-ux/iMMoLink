from django.conf import settings
from django.db import models


class Favorite(models.Model):
    locataire = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favoris")
    annonce = models.ForeignKey("properties.Property", on_delete=models.CASCADE, related_name="favoris")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("locataire", "annonce")
        ordering = ["-created_at"]
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"

    def __str__(self):
        return f"{self.locataire} ♥ {self.annonce}"
