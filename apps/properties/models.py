from datetime import timedelta

from django.db import models
from django.utils import timezone


class Amenity(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    icone = models.CharField(
        max_length=40, blank=True,
        help_text="Classe d'icône Font Awesome (sans le préfixe fa-solid), ex. fa-shower",
    )

    class Meta:
        ordering = ["nom"]
        verbose_name = "Équipement"
        verbose_name_plural = "Équipements"

    def __str__(self):
        return self.nom


class Property(models.Model):
    TYPE_CHOICES = [
        ("chambre", "Chambre"),
        ("studio", "Studio"),
        ("appartement", "Appartement"),
        ("maison", "Maison"),
        ("villa", "Villa"),
        ("autre", "Autre"),
    ]
    PERIOD_CHOICES = [
        ("mensuel", "Mensuel"),
        ("trimestriel", "Trimestriel"),
        ("annuel", "Annuel"),
    ]
    STATUT_CHOICES = [
        ("brouillon", "Brouillon"),
        ("en_attente_validation", "En attente de validation"),
        ("validee", "Validée"),
        ("publiee", "Publiée"),
        ("refusee", "Refusée"),
        ("suspendue", "Suspendue"),
        ("louee", "Louée"),
    ]
    DISPONIBILITE_CHOICES = [
        ("disponible", "Disponible"),
        ("indisponible", "Indisponible"),
    ]

    proprietaire = models.ForeignKey(
        "accounts.OwnerProfile", on_delete=models.CASCADE, related_name="annonces"
    )
    titre = models.CharField(max_length=200)
    description = models.TextField()
    type_logement = models.CharField(max_length=20, choices=TYPE_CHOICES)
    prix = models.DecimalField(max_digits=12, decimal_places=0)  # XOF, jamais de décimale
    periodicite = models.CharField(max_length=20, choices=PERIOD_CHOICES, default="mensuel")
    caution = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    chambres = models.PositiveSmallIntegerField(default=1)

    # --- Localisation (remplace les anciens champs texte libre ville / quartier) ---
    commune = models.ForeignKey(
        "geo.Commune",
        on_delete=models.PROTECT,
        related_name="properties",
        help_text="Remplace l'ancien champ libre 'ville'",
    )
    quartier = models.ForeignKey(
        "geo.Locality",
        on_delete=models.PROTECT,
        related_name="properties",
        help_text="Remplace l'ancien champ libre 'quartier' (village ou quartier)",
    )
    adresse = models.CharField(max_length=255, blank=True)

    statut = models.CharField(max_length=30, choices=STATUT_CHOICES, default="brouillon")
    disponibilite = models.CharField(max_length=30, choices=DISPONIBILITE_CHOICES, default="disponible")
    motif_refus = models.TextField(blank=True)
    amenities = models.ManyToManyField(
        Amenity, through="PropertyAmenity", related_name="properties", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    publiee_le = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Annonce"
        verbose_name_plural = "Annonces"
        indexes = [
            models.Index(fields=["commune"]),
            models.Index(fields=["quartier"]),
        ]

    def __str__(self):
        return self.titre

    @property
    def photo_principale(self):
        image = self.images.filter(principale=True).first() or self.images.first()
        return image.fichier if image else None

    @property
    def est_nouvelle(self):
        return bool(self.publiee_le) and (timezone.now() - self.publiee_le) < timedelta(days=7)


class PropertyImage(models.Model):
    annonce = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    fichier = models.ImageField(upload_to="properties/")
    principale = models.BooleanField(default=False)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordre", "id"]
        verbose_name = "Photo d'annonce"
        verbose_name_plural = "Photos d'annonce"

    def __str__(self):
        return f"Photo #{self.pk} — {self.annonce.titre}"


class PropertyAmenity(models.Model):
    annonce = models.ForeignKey(Property, on_delete=models.CASCADE)
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("annonce", "amenity")
        verbose_name = "Équipement d'annonce"
        verbose_name_plural = "Équipements d'annonce"