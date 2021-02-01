from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, AbstractUser
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from PIL import Image
from phonenumber_field.modelfields import PhoneNumberField #requires phonenumbers module

from .utils import generate_ref_code, generate_otp_number


STATUS = (
    ("Male", "Male"),
    ("Female", "Female")
)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)
    mobile = PhoneNumberField()
    otp = models.CharField(max_length=6)
    bio = models.TextField(blank=True)
    code = models.CharField(max_length=8, blank=True)
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
        return f"{self.user.username}-{self.code}"
    
    class Meta:
        verbose_name_plural = "User Profile"
        
    def get_recommend_profiles(self):
        qs = Profile.objects.all()
        my_recs = [p for p in qs if p.recommended_by == self.user]
        return my_recs
        
    def save(self, *args, **kwargs):
        if self.code == "":
            code = generate_ref_code()
            self.code = code

        if self.otp == "":
            otp = generate_otp_number()
            self.otp = otp
        
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