# Generated by Django 3.1.7 on 2021-04-02 05:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wallet', '0011_auto_20210402_0650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]