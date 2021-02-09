from django.shortcuts import render, redirect, reverse

from django.contrib.auth import login, authenticate
from django.contrib.auth import get_user_model
CustomUser = get_user_model()
from django.views.generic import ListView, TemplateView, View

# for the signup view
from django.conf import settings
from django.core.mail import EmailMessage
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404

import json
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import FormView
from .authy import send_verification_code, verify_sent_code

from .forms import (
    CustomSignUpForm,
    PhoneVerificationForm,
    CustomLoginForm,
    UniqueTagForm,
    UserUpdateForm,
    ProfileUpdateForm,
    CustomPasswordChangeForm
                    )
from .tokens import account_activation_token
from .models import Profile, Notification

import random
import threading


class EmailThread(threading.Thread):
    
    def __init__(self, send_email):
        self.send_email = send_email
        threading.Thread.__init__(self)

    def run(self):
        self.send_email.send(fail_silently=False)

def account_settings_update(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST or None, instance=request.user)
        p_form = ProfileUpdateForm(request.POST or None,
                        request.FILES or None,
                        instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'{request.user.unique_tag} account was updated.')
            return redirect('accounts:account-settings')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)  
        context = {
            'u_form': u_form,
            'p_form': p_form
        }
        return render(request, "accounts/account_settings.html", context)

class AccountSettings(LoginRequiredMixin, View):
    def get(self, request):
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)  
        context = {
            'u_form': u_form,
            'p_form': p_form
        }
        return render(request, "accounts/account_settings.html", context)
    
    def post(self, request):
        # Check for 2factor security
        if 'two_factor_auth' in request.POST:
            if request.user.two_factor_auth:
                request.user.two_factor_auth = False
                messages.warning(request, "You have disabled 2factor security")
            else:
                request.user.two_factor_auth = True
                messages.info(request, "You have enabled 2factor security")
            request.user.save()
        else:
            pass #then return redirect.
        
            # User update form
            u_form = UserUpdateForm(request.POST or None, instance=request.user)
            p_form = ProfileUpdateForm(request.POST or None,
                            request.FILES or None,
                            instance=request.user.profile)
            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request, f'{request.user.unique_tag} account was updated.')
        return redirect('accounts:account-settings')

    
    
    


class CustomSignupView(SuccessMessageMixin, FormView):
    template_name = 'accounts/signup.html'
    form_class = CustomSignUpForm
    success_message = "One-Time password sent to your registered mobile number.\
                       The verification code is valid for 10 minutes."

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            messages.info(
                self.request, f"{self.request.user} you are logged in")
            return redirect('accounts:profile-view')
        else:
            return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Get the profile session_key
        profile_id = self.request.session.get('ref_profile')
        
        if form.is_valid():
            user = form.save()

        phone_number = self.request.POST.get('phone_number')
        password = self.request.POST.get('password1')
        authenticate(phone_number=phone_number, password=password)
        try:
            response = send_verification_code(user)
            messages.add_message(
                self.request, messages.INFO, self.success_message)
        except Exception as e:
            messages.add_message(self.request, messages.WARNING,
                                 'verification code not sent. \n'
                                 'Please re-register.')
            user.delete() #make sure user not saved
            return redirect('accounts:signup')
        data = json.loads(response.text)

        # print(response.status_code, response.reason)
        # print(response.text)
        # print(data['success'])
        
        if data.get('success') == False:
            messages.add_message(self.request, messages.WARNING,
                                 data.get('message'))
            return redirect('accounts:signup')
        else:
            # Implement web_ref_code before calling verification_view:
            if profile_id is not None:
                recommended_by_profile = Profile.objects.get(id=profile_id)
                instance = form.save()
                registered_user = CustomUser.objects.get(id=instance.id)
                registered_profile = Profile.objects.get(user=registered_user)
                registered_profile.recommended_by = recommended_by_profile.user
                registered_profile.save()
            else:
                pass
            
            kwargs = {'user': user}
            return phone_verification_view(self.request, **kwargs)


def phone_verification_view(request, **kwargs):
    template_name = 'accounts/phone_confirm.html'

    if request.user.is_authenticated:
        messages.info(
            request, f"{request.user} you are logged in")
        return redirect('accounts:profile-view')

    if request.method == "POST":
        phone_number = request.POST.get('phone_number')
        user = CustomUser.objects.get(phone_number=phone_number)

        form = PhoneVerificationForm(request.POST or None)
        if form.is_valid():
            verification_code = form.cleaned_data.get('one_time_password')
            response = verify_sent_code(verification_code, user)

            # print(response.text)
            data = json.loads(response.text)
            if data.get('success') == True:
                if user.is_active == False:
                    user.is_active = True
                    user.save()
                    
                login(request, user)
                    
                if user.phone_number_verified is False:
                    user.phone_number_verified = True
                    user.save()
                    
                # check for unique_tag before accessing dashboard...
                if user.unique_tag:
                    return redirect('accounts:profile-view')
                else:
                    return redirect('accounts:unique-tag')
            else:
                messages.add_message(request, messages.WARNING,
                                     data.get('message'))
                return render(request, template_name, {'user': user})
        else:
            context = {
                'user': user,
                'form': form,
            }
            return render(request, template_name, context)

    elif request.method == "GET":
        try:
            user = kwargs.get('user')
            if user:
                return render(request, template_name, {'user': user})
            return HttpResponse("<h4>Not Allowed!</h4>")
        except:
            return HttpResponse("<h4>Not Allowed!</h4>")


class CustomLoginView(SuccessMessageMixin, FormView):
    template_name = 'registration/login.html'
    form_class = CustomLoginForm
    success_url = '/accounts/profile/'
    success_message = "One-Time password sent to your registered mobile number.\
                       The verification code is valid for 10 minutes."

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            messages.info(
                self.request, f"{self.request.user.unique_tag} you are logged in")
            return redirect('accounts:profile-view')
        else:
            return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if form.is_valid():
            user = form.login(self.request)
        
        if user.two_factor_auth is False:
            login(self.request, user)
            # check for unique_tag before accessing dashboard...
            if user.unique_tag:
                return redirect('accounts:profile-view')
            else:
                return redirect('accounts:unique-tag')
        else:
            try:
                response = send_verification_code(user)
                messages.add_message(
                    self.request, messages.INFO, self.success_message)
            except Exception as e:
                messages.info(
                    self.request, "Verifacation code not sent. \n Please retry logging in")
                return redirect('accounts:login')
            data = json.loads(response.text)

            if data.get('success') == False:
                messages.info(
                    self.request, data.get('message'))
                return redirect('accounts:login')
            # print(response.status_code, response.reason)
            # print(response.text)

            if data.get('success') == True:
                kwargs = {'user': user}
                return phone_verification_view(self.request, **kwargs)
            else:
                messages.add_message(self.request, messages.WARNING,
                                     data.get('message'))
                return redirect('accounts:login')

@login_required
def set_unique_tag(request):
    template_name = 'accounts/unique_tag.html'
    if request.method == "POST":
        phone_number = request.POST.get('phone_number')
        user = CustomUser.objects.get(phone_number=phone_number)
        
        form = UniqueTagForm(request.POST or None)
        if form.is_valid():
            raw_unique_tag = form.cleaned_data.get('unique_tag')
            user.unique_tag = raw_unique_tag
            user.save()
            messages.success(request, f"{user.unique_tag} saved")
            return redirect('accounts:profile-view')
    else:
        form = UniqueTagForm()
        context = {'form': form}
        return render(request, template_name, context)

@method_decorator(login_required(login_url="{% url 'accounts:login' %}"), name="dispatch")
class DashboardView(SuccessMessageMixin, View):
    template_name = "accounts/profile_view.html"

    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        my_recs = profile.get_recommend_profiles()
        current_site = get_current_site(self.request)
        domain = current_site.domain
        # get notifications
        notifications = Notification.objects.all()
        context = {
            'user': self.request.user,
            'host':domain,
            'my_recs':my_recs,
            'notifications':notifications
        }
        if not request.user.phone_number_verified:
            messages.info(self.request, f"{self.request.user.phone_number} Not verified.")
        return render(self.request, self.template_name, context)
        # post method used in accounts/account-settings view


class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = "registration/password_change.html"
    success_url = reverse_lazy('accounts:account-settings')
    

def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    notification.viewed =  True
    notification.save()
    return redirect('accounts:profile-view')


# def signup(request):
#     profile_id = request.session.get('ref_profile')
#     form = CustomSignUpForm(request.POST or None)
#     if form.is_valid():
#         user = form.save(commit=False)
#         user.is_active = False
#         user.save()
#         # adding the mobile while signup
#         user.refresh_from_db()
#         user.profile.mobile = form.cleaned_data.get('mobile')
#         user.save()

#         # for email confirmation
#         raw_email = form.cleaned_data.get('email')
#         domain = get_current_site(request).domain
#         uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
#         token = account_activation_token.make_token(user)
#         link = reverse('accounts:activate', kwargs={'uidb64': uidb64, 'token': token})
#         activate_url = domain+link

#         email_subject = 'Activate Your Easypay Account.'
#         email_body = f'Hi {user.username} Please use this link to activate your account,\n If you are unable to click the link copy it to a new browser tab.\n\n{activate_url}'
#         send_email = EmailMessage(
#             email_subject,
#             email_body,
#             'noreply@easypay.com',
#             [raw_email],
#         )
#         EmailThread(send_email).start()

#         # for the referal
#         if profile_id is not None:
#             recommended_by_profile = Profile.objects.get(id=profile_id)
#             form = CustomSignUpForm()
#             instance = form.save()
#             registered_user = CustomUser.objects.get(id=instance.id)
#             registered_profile = Profile.objects.get(user=registered_user)
#             registered_profile.recommended_by = recommended_by_profile.user
#             registered_profile.save()
#             messages.info(
#                 request, "An email has been sent to your mailbox...")
#             return redirect('/')
#         else:
#             messages.info(
#                 request, "An email has been sent to your mailbox...")
#             return redirect('/')

#     context = {'form': form}
#     return render(request, 'accounts/signup.html', context)
    

# def activate(request, uidb64, token):
#     try:
#         uid = force_text(urlsafe_base64_decode(uidb64))
#         user = CustomUser.objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
#         user = None
    
#     if user is not None and account_activation_token.check_token(user, token):
#         user.is_active = True
#         user.profile.email_confirmed = True
#         user.save()
#         login(request, user)
#         return redirect('accounts:profile-view')
#     return redirect('/')

    