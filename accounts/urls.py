from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.dispatch import receiver
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed
    )
from django.contrib.auth.models import User
from django.contrib import messages
from .views import (
    signup,
    ProfileView,
    CustomPasswordChangeView,
    account_settings,
    activate,
    AuthView
)

app_name = "accounts"

@receiver(user_logged_in, sender=User)
def user_logged_in_info(sender, user, request, **kwargs):
    if user:
        msg = "Successfully logged in {user}.".format(user=request.user.username)
    else:
        msg = "Logged in successfully"
    messages.add_message(request, messages.INFO, msg)

@receiver(user_logged_out, sender=User)
def user_logout_in_info(sender, user, request, **kwargs):
    if user:
        msg = f"{user.username} logged out."
    else:
        msg = "Logged out successfully"
    messages.add_message(request, messages.INFO, msg)
    
@receiver(user_login_failed)
def user_login_failed_info(request, **kwargs):
    user = request.user
    if user:
        msg = "You have entered an invalid credentials!"
    else:
        msg = "Invalid credentials!"
    messages.add_message(request, messages.WARNING, msg)

urlpatterns = [
    path('auth-view/', AuthView.as_view(), name="auth-view"),
    path('signup/', signup, name="signup"),
    path('login/', auth_views.LoginView.as_view(), name="login"),
    path('profile/', ProfileView.as_view(), name="profile-view"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('password-change/', CustomPasswordChangeView.as_view(), name="password-change"),
    path('account-settings/', account_settings, name="account-settings"),
    path('activate/<uidb64>/<token>/', activate, name="activate"),
]
