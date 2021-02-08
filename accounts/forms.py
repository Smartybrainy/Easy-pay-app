from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.views import PasswordChangeForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext as _
from .models import CustomUser
from .models import Profile


COUNTRY_CODE = (
    (234, 'Nigeria (+234)'),
    (233, 'Ghana (+233)')
)


class CustomSignUpForm(UserCreationForm):
    unique_tag = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={
        'placeholder': 'unique_tag, e.g #name'
    }))
    password1 = forms.CharField(max_length=14, widget=forms.PasswordInput(attrs={
        'placeholder': "password"
    }))
    password2 = forms.CharField(max_length=14, widget=forms.PasswordInput(attrs={
        'placeholder': "confirm password"
    }))
    phone_number = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={
        'placeholder': "mobile mumber"
    }))
    country_code = forms.ChoiceField(choices=COUNTRY_CODE)
    # email = forms.EmailField(max_length=255, widget=forms.TextInput(attrs={
    #     'placeholder': "email: noreply.example.com"
    # }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for fieldname in ['phone_number', 'country_code', 'unique_tag', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].label = ''

    class Meta:
        model = CustomUser
        fields = ('phone_number', 'country_code', 'unique_tag', 'password1', 'password2')

    def clean_email(self):
        if self.email:
            email = self.cleaned_data.get('email')
            if CustomUser.objects.filter(email=email).exists():
                raise forms.ValidationError(
                    "A user with same email already exists.")
            return email
        else:
            pass
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError(
                _("Another user with this phone number already exists please try another"))
        return phone_number
    
    
class PhoneVerificationForm(forms.Form):
    one_time_password = forms.IntegerField()

    class Meta:
        help_texts = {'one_time_password': None}
        fields = ['one_time_password', ]
  
    
class CustomLoginForm(forms.Form):
    phone_number = forms.IntegerField(widget=forms.NumberInput(attrs={
        'placeholder': 'mobile number',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'password'
    }))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in self.fields:
            self.fields[fieldname].label = ''

    class Meta:
        fields = ['phone_number', 'password']

    def clean(self):
        phone_number = self.cleaned_data.get('phone_number')
        password = self.cleaned_data.get('password')
        user = authenticate(phone_number=phone_number, password=password)
        if not user:
            raise forms.ValidationError(
                "Sorry, your login was invalid. Please try again.")
        return self.cleaned_data

    def login(self, request):
        phone_number = self.cleaned_data.get('phone_number')
        password = self.cleaned_data.get('password')
        try:
            user = authenticate(phone_number=phone_number, password=password)
            return user
        except:
            raise forms.ValidationError(
                "Sorry, your login was invalid. Please try again.")


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=False)
    unique_tag = forms.CharField(required=False)

    class Meta:
        model = CustomUser
        help_texts = {'unique_tag': None}
        fields = ['phone_number', 'unique_tag', 'email']


class ProfileUpdateForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    gender = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': "Male/Female"
    }))

    class Meta:
        model = Profile
        fields = ['gender', 'image']
        
        
class CustomPasswordChangeForm(PasswordChangeForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in self.fields:
            self.fields[fieldname].help_text = None
          
    class Meta:
        model = CustomUser
        fields = '__all__'
            

class CustomUserCreationForm(UserCreationForm):
    
    class Meta:
        class Meta(UserCreationForm.Meta):
            model = CustomUser
            fields = ('phone_number',)
        
        
class CustomChangeForm(UserChangeForm):
    
    class Meta:
        model = CustomUser
        fields = ('phone_number',)
        