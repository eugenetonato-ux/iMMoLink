from django.db import models


class Department(models.Model):
    """Département (ex. Littoral, Atlantique...)."""

    nom = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["nom"]
        verbose_name = "Département"
        verbose_name_plural = "Départements"

    def __str__(self):
        return self.nom


class Commune(models.Model):
    """Commune, rattachée à un département (ex. Cotonou, Abomey-Calavi...)."""

    nom = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="communes"
    )

    class Meta:
        ordering = ["nom"]
        unique_together = ("nom", "department")
        verbose_name = "Commune"
        verbose_name_plural = "Communes"

    def __str__(self):
        return self.nom


class Arrondissement(models.Model):
    """Arrondissement, rattaché à une commune."""

    nom = models.CharField(max_length=150)
    commune = models.ForeignKey(
        Commune, on_delete=models.CASCADE, related_name="arrondissements"
    )

    class Meta:
        ordering = ["nom"]
        unique_together = ("nom", "commune")
        verbose_name = "Arrondissement"
        verbose_name_plural = "Arrondissements"

    def __str__(self):
        return self.nom


class Locality(models.Model):
    """Village ou quartier, rattaché à un arrondissement.

    C'est ce niveau qui remplace le champ libre `quartier` sur Property.
    """

    TYPE_CHOICES = [
        ("village", "Village"),
        ("quartier", "Quartier"),
    ]

    nom = models.CharField(max_length=200)
    locality_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default="quartier"
    )
    arrondissement = models.ForeignKey(
        Arrondissement, on_delete=models.CASCADE, related_name="localities"
    )

    class Meta:
        ordering = ["nom"]
        unique_together = ("nom", "arrondissement")
        verbose_name = "Village / Quartier"
        verbose_name_plural = "Villages / Quartiers"

    def __str__(self):
        return self.nom

    @property
    def commune(self):
        return self.arrondissement.commune

    @property
    def department(self):
        return self.arrondissement.commune.department