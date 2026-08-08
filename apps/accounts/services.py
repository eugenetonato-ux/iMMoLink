from .models import OwnerProfile, TenantProfile, User


def attribuer_role(user, role):
    """Attribue le rôle locataire/propriétaire à un utilisateur, juste après sa
    connexion Google. Le rôle 'admin' n'existe pas dans ROLE_CHOICES : il est
    donc structurellement impossible de l'attribuer depuis cette fonction.
    Une fois choisi, le rôle est figé (pas de changement en libre-service)."""
    valeurs_autorisees = {choice for choice, _ in User.ROLE_CHOICES}
    if role not in valeurs_autorisees:
        raise ValueError("Rôle invalide.")

    if user.role and user.role != role:
        # Le rôle est déjà défini : on ne l'écrase pas silencieusement.
        return user

    if not user.role:
        user.role = role
        user.save(update_fields=["role"])

    if role == "locataire":
        TenantProfile.objects.get_or_create(user=user)

    return user


def profil_proprietaire_complet(user):
    """Un profil propriétaire est complet quand WhatsApp, ville, quartier et
    photo de profil (upload manuel obligatoire) sont renseignés."""
    try:
        profil = user.ownerprofile
    except OwnerProfile.DoesNotExist:
        return False
    return bool(profil.whatsapp and profil.ville and profil.quartier and profil.photo_profil)


def creer_ou_maj_profil_proprietaire(user, whatsapp, ville, quartier, adresse="", photo_profil=None):
    profil, _ = OwnerProfile.objects.get_or_create(user=user)
    if whatsapp:
        profil.whatsapp = whatsapp
    if ville:
        profil.ville = ville
    if quartier:
        profil.quartier = quartier
    if adresse:
        profil.adresse = adresse
    if photo_profil:
        profil.photo_profil = photo_profil
    profil.save()
    return profil
