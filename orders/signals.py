from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Restaurant


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Get first restaurant (or create default one)
        restaurant = Restaurant.objects.first()
        if not restaurant:
            restaurant = Restaurant.objects.create(name="Default Restaurant")

        # Default role = owner (you can change logic later)
        UserProfile.objects.create(
            user=instance,
            restaurant=restaurant,
            role = "kitchen" if instance.username == "kitchen" else "owner"
        )
