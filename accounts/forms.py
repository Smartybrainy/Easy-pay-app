from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm
from .models import User
from .models import Profile

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        class Meta(UserCreationForm.Meta):
             model = User
             fields = ('username',)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=150, help_text="Required. Inform of valid email")
    
    class Meta:
        model = User
        help_texts={'username':None,}
        fields = ('email', 'username', 'phone', 'password1', 'password2')
        

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=False)
    username = forms.CharField(required=False)

    class Meta:
        model = User
        help_texts = {'username': None}
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    gender = forms.CharField(required=False)

    class Meta:
        model = Profile
        fields = ['gender', 'image']