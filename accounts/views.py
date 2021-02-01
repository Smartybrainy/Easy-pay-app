from django.shortcuts import render, redirect, reverse

from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
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
from .forms import SignUpForm, UserUpdateForm, ProfileUpdateForm, CustomPasswordChangeForm
from .tokens import account_activation_token
from .models import Profile

import http.client
import random
import threading


def send_otp(mobile, otp):
    conn = http.client.HTTPSConnection("2factor.in")
    api_authkey = settings._2FACTOR_APIKEY
    _2factor_template_name = settings._2FACTOR_TEMPLATE_NAME
    headers = {'content-type': "application/json"}

    url_2factor = "https://2factor.in/API/R1/?module=SMS_OTP&apikey=4145c29c-5e75-11eb-8153-0200cd936042&to=" + \
        mobile+"&otpvalue="+otp+"templatename=OtpValidation"

    # conn = http.client.HTTPSConnection("api.msg91.com")
    # url_msg91 = "http://control.msg91.com/api/sendotp.php?otp" + \
    #     otp+"&sender=ABC&message="+"Your OTP is " + \
    #         otp+"&mobile= "+mobile+"&authkey="+authkey+"&country=234"

    conn.request("GET", url_2factor, headers=headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    return None


class EmailThread(threading.Thread):
    
    def __init__(self, send_email):
        self.send_email = send_email
        threading.Thread.__init__(self)

    def run(self):
        self.send_email.send(fail_silently=False)

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


class AuthView(TemplateView):
    template_name="accounts/auth_view.html"


def signup(request):
    profile_id = request.session.get('ref_profile')
    form = SignUpForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        # adding the mobile while signup
        user.refresh_from_db()
        user.profile.mobile = form.cleaned_data.get('mobile')
        user.save()

        # For otp, send_otp func above
        mobile = form.cleaned_data.get('mobile')
        otp = str(random.randint(1000, 9999))
        send_otp(mobile, otp)
        request.session['mobile'] = mobile

        # for email confirmation
        raw_email = form.cleaned_data.get('email')
        domain = get_current_site(request).domain
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        link = reverse('accounts:activate', kwargs={'uidb64': uidb64, 'token': token})
        activate_url = domain+link

        email_subject = 'Activate Your Easypay Account.'
        email_body = f'Hi {user.username} Please use this link to activate your account,\n If you are unable to click the link copy it to a new browser tab.\n\n{activate_url}'
        send_email = EmailMessage(
            email_subject,
            email_body,
            'noreply@easypay.com',
            [raw_email],
        )
        EmailThread(send_email).start()

        # for the referal
        if profile_id is not None:
            recommended_by_profile = Profile.objects.get(id=profile_id)
            form = SignUpForm()
            instance = form.save()
            registered_user = User.objects.get(id=instance.id)
            registered_profile = Profile.objects.get(user=registered_user)
            registered_profile.recommended_by = recommended_by_profile.user
            registered_profile.save()
            messages.info(
                request, "An email has been sent to your mailbox...")
            return redirect('/')
        else:
            messages.info(
                request, "An email has been sent to your mailbox...")
            return redirect('/')

    context = {'form': form}
    return render(request, 'accounts/signup.html', context)
    

class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = "registration/password_change.html"
    success_url = reverse_lazy('accounts:login')
    

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
    return redirect('/')

    