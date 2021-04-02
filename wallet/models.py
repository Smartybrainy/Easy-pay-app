from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
CustomUser = settings.AUTH_USER_MODEL


class Wallet(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    balance = models.FloatField(blank=True, null=True)
    created = models.BooleanField(default=True)
    added_date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s : %s" % (self.user.unique_tag, self.balance)

    class Meta:
        verbose_name_plural = _("Wallet balance")
