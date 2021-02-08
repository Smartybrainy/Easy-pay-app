# from django.contrib.auth.models import UserManager
from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    user_in_migrations = True

    def _create_user(self, phone_number, email, password, **extra_fields):

        if not phone_number:
            raise ValueError("The given phone number must be set")
        email = self.normalize_email(email)
        user = self.model(phone_number=phone_number, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone_number, email, password, **extra_fields)

    def create_superuser(self, phone_number, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone_number, email, password, **extra_fields)