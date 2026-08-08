from django.db import models
from django.utils.text import slugify


class Ville(models.Model):
    """Référentiel des villes du Bénin utilisé par la recherche et la création d'annonce."""

    nom = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    photo = models.ImageField(upload_to="locations/villes/", blank=True, null=True)
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage (villes populaires).")
    est_populaire = models.BooleanField(default=False)

    class Meta:
        ordering = ["ordre", "nom"]
        verbose_name = "Ville"
        verbose_name_plural = "Villes"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom


class Quartier(models.Model):
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE, related_name="quartiers")
    nom = models.CharField(max_length=100)

    class Meta:
        ordering = ["nom"]
        unique_together = ("ville", "nom")
        verbose_name = "Quartier"
        verbose_name_plural = "Quartiers"

    def __str__(self):
        return f"{self.nom} ({self.ville.nom})"
