from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import Profile, Notification


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, *args, **kwargs):
    instance.profile.save()
    
    
@receiver(post_save, sender=User)
def create_notification(sender, **kwargs):
    if kwargs.get('created', False):
        Notification.objects.create(user=kwargs.get('instance'), title="Welcome to EasyPay", content="Thanks for signing up! \n Please provide your email in the account settings for easy password reset.")
