from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ClientProfile, User


@receiver(post_save, sender=User)
def create_client_profile(sender, instance, created, **kwargs):
    if created:
        ClientProfile.objects.create(user=instance)