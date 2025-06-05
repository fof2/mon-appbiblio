from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Panier

@receiver(post_save, sender=User)
def creer_panier_utilisateur(sender, instance, created, **kwargs):
    if created:
        Panier.objects.create(utilisateur=instance)
