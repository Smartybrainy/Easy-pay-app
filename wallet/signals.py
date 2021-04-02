from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
from django.contrib.auth import get_user_model
CustomUser = get_user_model()

from .models import Wallet


@receiver(post_save, sender=CustomUser)
def create_wallet(sender, *args, **kwargs):
    if kwargs.get('created', False):
        Wallet.objects.create(user=kwargs.get('instance'),
        balance=kwargs.get('balance'),
        added_date=timezone.now
        )




