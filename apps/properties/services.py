from django.conf import settings
from django.core.mail import send_mail

from .models import Property, PropertyImage


def enregistrer_annonce(profil, annonce, data, files):
    """Crée ou met à jour une annonce en brouillon à partir du formulaire propriétaire."""
    if annonce is None:
        annonce = Property(proprietaire=profil, statut="brouillon")

    annonce.titre = data.get("titre", "").strip()
    annonce.description = data.get("description", "").strip()
    annonce.type_logement = data.get("type_logement", "")
    annonce.prix = data.get("prix") or 0
    annonce.periodicite = data.get("periodicite", "mensuel")
    annonce.caution = data.get("caution") or None
    annonce.chambres = data.get("chambres") or 1
    annonce.ville = data.get("ville", "").strip()
    annonce.quartier = data.get("quartier", "").strip()
    annonce.adresse = data.get("adresse", "").strip()
    if not annonce.pk:
        annonce.statut = "brouillon"
    annonce.save()

    amenity_ids = data.getlist("amenities") if hasattr(data, "getlist") else []
    annonce.amenities.set(amenity_ids)

    photos = files.getlist("photos") if hasattr(files, "getlist") else []
    a_deja_une_principale = annonce.images.filter(principale=True).exists()
    for index, fichier in enumerate(photos):
        PropertyImage.objects.create(
            annonce=annonce,
            fichier=fichier,
            principale=(index == 0 and not a_deja_une_principale),
            ordre=annonce.images.count(),
        )

    return annonce


def supprimer_photo(annonce, image_id):
    annonce.images.filter(pk=image_id).delete()


def soumettre_pour_validation(annonce):
    """Passe l'annonce en attente de validation et notifie l'admin par email
    (backend console en local — voir EMAIL_BACKEND dans settings)."""
    annonce.statut = "en_attente_validation"
    annonce.save(update_fields=["statut"])

    if settings.ADMIN_NOTIFICATION_EMAIL:
        send_mail(
            subject=f"[iMMoLink] Nouvelle annonce à valider — {annonce.titre}",
            message=(
                f"{annonce.proprietaire.user.email} a soumis « {annonce.titre} » "
                f"({annonce.ville}, {annonce.quartier}) pour validation.\n\n"
                f"Voir dans l'espace admin : /{settings.ADMIN_URL_PATH}/annonces/"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL or None,
            recipient_list=[settings.ADMIN_NOTIFICATION_EMAIL],
            fail_silently=True,
        )
    return annonce


def retirer_annonce(annonce):
    """Retire une annonce publiée du marché à la demande du propriétaire :
    elle repasse en brouillon (donc redevient modifiable) et perd sa date de
    publication. Elle pourra être renvoyée en validation plus tard."""
    annonce.statut = "brouillon"
    annonce.publiee_le = None
    annonce.save(update_fields=["statut", "publiee_le"])
    return annonce