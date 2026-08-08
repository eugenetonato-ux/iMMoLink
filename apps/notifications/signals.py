from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from apps.accounts.models import User


@receiver(pre_save, sender=User)
def _track_previous_role(sender, instance, **kwargs):
    """Mémorise le rôle avant sauvegarde pour détecter le passage vide -> rempli."""
    if instance.pk:
        try:
            instance._previous_role = User.objects.get(pk=instance.pk).role
        except User.DoesNotExist:
            instance._previous_role = None
    else:
        instance._previous_role = None


@receiver(post_save, sender=User)
def notify_admin_new_signup(sender, instance, created, **kwargs):
    """Notifie l'admin uniquement quand l'utilisateur vient de choisir son rôle
    (fin réelle du parcours d'inscription), pas à chaque connexion ni à chaque save."""
    previous_role = getattr(instance, "_previous_role", None)

    if not created and not previous_role and instance.role:
        send_mail(
            subject=f"[iMMoLink] Nouvelle inscription : {instance.email}",
            message=(
                f"Un nouvel utilisateur a terminé son inscription.\n\n"
                f"Email : {instance.email}\n"
                f"Rôle choisi : {instance.get_role_display()}\n"
                f"Date : {instance.date_joined}\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_NOTIFICATION_EMAIL],
            fail_silently=False,
        )
