from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ("locataire", "Locataire"),
        ("proprietaire", "Propriétaire"),
    ]
    email = models.EmailField(unique=True)
    photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True)
    # role="admin" n'est jamais définissable via une vue publique/API — uniquement via script/DB


class OwnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    whatsapp = models.CharField(max_length=30)
    # --- Localisation : FK vers geo.Department / geo.Commune / geo.Arrondissement / geo.Locality ---
    # null=True car OwnerProfile est créé vide via get_or_create avant que le propriétaire
    # ne remplisse le formulaire ; profil_proprietaire_complet() vérifie leur présence.
    department = models.ForeignKey(
        "geo.Department", on_delete=models.PROTECT, related_name="owner_profiles",
        null=True, blank=True,
    )
    commune = models.ForeignKey(
        "geo.Commune", on_delete=models.PROTECT, related_name="owner_profiles",
        null=True, blank=True,
        help_text="Remplace l'ancien champ libre 'ville'",
    )
    arrondissement = models.ForeignKey(
        "geo.Arrondissement", on_delete=models.PROTECT, related_name="owner_profiles",
        null=True, blank=True,
    )
    quartier = models.ForeignKey(
        "geo.Locality", on_delete=models.PROTECT, related_name="owner_profiles",
        null=True, blank=True,
        help_text="Remplace l'ancien champ libre 'quartier' (village ou quartier)",
    )
    adresse = models.CharField(max_length=255, blank=True)
    photo_profil = models.ImageField(upload_to="profiles/owners/")  # upload manuel obligatoire
    verifie = models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_full_name() or self.user.email


class TenantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ville = models.CharField(max_length=100, blank=True)
    quartier = models.CharField(max_length=100, blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.email