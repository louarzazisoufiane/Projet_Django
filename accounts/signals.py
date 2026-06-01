"""Create a ProfilClient automatically for every new client account."""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Utilisateur, ProfilClient


@receiver(post_save, sender=Utilisateur)
def create_profil_client(sender, instance, created, **kwargs):
    if created:
        ProfilClient.objects.get_or_create(utilisateur=instance)
