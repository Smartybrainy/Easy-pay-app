from django.shortcuts import render
from django.http import HttpResponse
import http.client
import json
import requests
import ast

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status, generics
from .models import User, PhoneOTP
from django.shortcuts import get_object_or_404, redirect
import random

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import ListView, TemplateView, View
# for the signup view
from django.core.mail import EmailMessage
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .forms import SignUpForm, UserUpdateForm, ProfileUpdateForm
from .tokens import account_activation_token
from .models import Profile

conn = http.client.HTTPConnection("2factor.in")


class ValidatePhoneSendOTP(APIView):
    
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone')
        password = request.data.get('password', False)
        username = request.data.get('username', False)
        email    = request.data.get('email', False)

        if phone_number:
            phone = str(phone_number)
            user = User.objects.filter(phone__iexact = phone)
            if user.exists():
                return Response({
                    'status' : False,
                    'detail' : 'Phone number already exists'
                })

            else:
                key = send_otp(phone)
                if key:
                    old = PhoneOTP.objects.filter(phone__iexact = phone)
                    if old.exists():
                        old = old.first()
                        count = old.count
                        if count > 10:
                            return Response({
                                'status' : False,
                                'detail' : 'Sending otp error. Limit Exceeded. Please Contact Customer support'
                            })

                        old.count = count +1
                        old.save()
                        print('Count Increase', count)

                        conn.request("GET", "https://2factor.in/API/R1/?module=SMS_OTP&apikey=1028fcd9-3158-11ea-9fa5-0200cd936042&to="+phone+"&otpvalue="+str(key)+"&templatename=WomenMark1")
                        res = conn.getresponse() 
                        
                        data = res.read()
                        data=data.decode("utf-8")
                        data=ast.literal_eval(data)
                        
                        
                        if data["Status"] == 'Success':
                            old.otp_session_id = data["Details"]
                            old.save()
                            print('In validate phone :'+old.otp_session_id)
                            return Response({
                                   'status' : True,
                                   'detail' : 'OTP sent successfully'
                                })    
                        else:
                            return Response({
                                  'status' : False,
                                  'detail' : 'OTP sending Failed'
                                }) 

                       


                    else:

                        obj=PhoneOTP.objects.create(
                            phone=phone,
                            otp = key,
                            email=email,
                            username=username,
                            password=password,
                        )
                        conn.request("GET", "https://2factor.in/API/R1/?module=SMS_OTP&apikey=1028fcd9-3158-11ea-9fa5-0200cd936042&to="+phone+"&otpvalue="+str(key)+"&templatename=WomenMark1")
                        res = conn.getresponse()    
                        data = res.read()
                        print(data.decode("utf-8"))
                        data=data.decode("utf-8")
                        data=ast.literal_eval(data)

                        if data["Status"] == 'Success':
                            obj.otp_session_id = data["Details"]
                            obj.save()
                            print('In validate phone :'+obj.otp_session_id)
                            return Response({
                                   'status' : True,
                                   'detail' : 'OTP sent successfully'
                                })    
                        else:
                            return Response({
                                  'status' : False,
                                  'detail' : 'OTP sending Failed'
                                })

                        
                else:
                     return Response({
                           'status' : False,
                            'detail' : 'Sending otp error'
                     })   

        else:
            return Response({
                'status' : False,
                'detail' : 'Phone number is not given in post request'
            })            


def send_otp(phone):
    if phone:
        key = random.randint(999,9999)
        print(key)
        return key
    else:
        return False
    

class ProfileView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = "accounts/profile_view.html"


@login_required
def account_settings(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST or None, instance=request.user)
        p_form = ProfileUpdateForm(request.POST or None,
                                   request.FILES or None,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'{request.user.username} account was updated.')
            return redirect('accounts:account-settings')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, "accounts/account_settings.html", context)
    
        
# --------auth views----------------
class AuthView(TemplateView):
    template_name = 'accounts/auth_view.html'


def signup(request):
    if request.method == "POST":
       form = SignUpForm(request.POST)    
       if form.is_valid():
           form.save()
           email = form.cleaned_data.get('email')
           raw_password = form.cleaned_data.get('password1')
           user = authenticate(email=email, password=raw_password)
           login(request, user)
           return redirect('accounts:profile-view')
    else:
        form = SignUpForm()
        return render(request, 'accounts/signup.html', {'form':form})
    

class CustomPasswordChangeView(PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = "registration/password_change.html"
    success_url = reverse_lazy('accounts:login')
    
    
def account_activation_sent(request):
    return render(request, 'accounts/account_activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('accounts:profile-view')
    else:
        return render(request, 'accounts/activation_invalid.html')
    
    