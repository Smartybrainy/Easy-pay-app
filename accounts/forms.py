from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import Profile


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=15, required=False, help_text=None)
    last_name = forms.CharField(
        max_length=15, required=False, help_text=None)
    email = forms.EmailField(
        max_length=255)
    mobile = forms.CharField(max_length=16, widget=forms.NumberInput(attrs={
        'placeholder': "mobile mumber"
    }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'mobile', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "A user with same email already exists.")
        return email

        

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=False)
    username = forms.CharField(required=False)

    class Meta:
        model = User
        help_texts = {'username': None}
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    gender = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': "Male/Female"
    }))

    class Meta:
        model = Profile
        fields = ['gender', 'image']
        