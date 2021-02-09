from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from PIL import Image
from phonenumber_field.modelfields import PhoneNumberField #requires phonenumbers module
# pip install django-phonenumber-field[phonenumbers]
from django.utils import timezone

from .utils import generate_ref_code
from .manager import CustomUserManager
from django.contrib.auth import get_user_model
User = settings.AUTH_USER_MODEL


STATUS = (
    ("Male", "Male"),
    ("Female", "Female")
)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    web_code = models.CharField(max_length=8, blank=True)
    recommended_by = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name='ref_by')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(default="naira-sign2.jpg", upload_to="profile_pics",
                              width_field="width_field", height_field="height_field")
    width_field = models.IntegerField(default=0)
    height_field = models.IntegerField(default=0)
    gender = models.CharField(choices=STATUS, max_length=6, blank=True)
    
    def __str__(self):
        return f"{self.user.unique_tag}-{self.web_code}"
    
    class Meta:
        verbose_name_plural = "User Profiles"
        
    def get_recommend_profiles(self):
        qs = Profile.objects.all()
        my_recs = [p for p in qs if p.recommended_by == self.user]
        return my_recs
        
    def save(self, *args, **kwargs):
        if self.web_code == "":
            new_code = generate_ref_code()
            self.web_code = new_code
            
        return super(Profile, self).save(*args, **kwargs)
        # for image
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
    
    def delete(self, *args, **kwargs):
        self.image.delete()
        return super().delete(*args, **kwargs)
    

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=150, blank=True)
    content = models.TextField()
    viewed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    
class CustomUser(AbstractBaseUser, PermissionsMixin):
    # username = None
    email = models.EmailField(_('email'), unique=True, blank=True, null=True)
    unique_tag = models.CharField(_('unique_tag'), max_length=20, unique=True)
    full_name = models.CharField(_('full name'), max_length=130, blank=True)
    is_staff = models.BooleanField(_('is_staff'), default=False)
    is_active = models.BooleanField(_('is_active'), default=False)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    phone_number_verified = models.BooleanField(default=False)
    phone_number = models.BigIntegerField(unique=True)
    country_code = models.IntegerField(default=234)
    two_factor_auth = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email','country_code','unique_tag']

    class Meta:
        ordering = ('email',)
        verbose_name = _('user',)
        verbose_name_plural = _('users')

    def get_short_name(self):
        if self.full_name != "":
            return self.full_name
        return self.unique_tag

    def __str__(self):
        return self.unique_tag