from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.dispatch import receiver
from django.contrib import messages
from django.contrib.auth import get_user_model
CustomUser = get_user_model()
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed
    )
from .views import (
    CustomSignupView,
    CustomLoginView,
    phone_verification_view,
    DashboardView,
    set_unique_tag,
    CustomPasswordChangeView,
    AccountSettings,
    verify_email,
    activate,
    delete_notification
)

app_name = "accounts"

@receiver(user_logged_in, sender=CustomUser)
def user_logged_in_info(sender, user, request, **kwargs):
    if user:
        msg = "Successfully logged in {user}.".format(user=request.user.unique_tag)
    else:
        msg = "Logged in successfully"
    messages.add_message(request, messages.INFO, msg)

@receiver(user_logged_out, sender=CustomUser)
def user_logout_in_info(sender, user, request, **kwargs):
    if user:
        msg = f"{user.unique_tag} logged out."
    else:
        msg = "Logged out successfully"
    messages.add_message(request, messages.INFO, msg)
    
@receiver(user_login_failed, sender=CustomUser)
def user_login_failed_info(sender, user, request, **kwargs):
    if user:
        msg = "Sorry, your login was invalid. Please try again.!"
    else:
        msg = "Invalid credentials!"
    messages.add_message(request, messages.WARNING, msg)

urlpatterns = [
    path('signup/', CustomSignupView.as_view(), name="signup"),
    path('login/', CustomLoginView.as_view(), name="login"),
    path('verify/', phone_verification_view, name="verify"),
    path('unique-tag/', set_unique_tag, name="unique-tag"),
    path('profile/', DashboardView.as_view(), name="profile-view"),
    path('account-settings/', AccountSettings.as_view(), name="account-settings"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('password-change/', CustomPasswordChangeView.as_view(), name="password-change"),
    path('verify-email/', verify_email, name="verify-email"),
    path('activate/<uidb64>/<token>/', activate, name="activate"),
    
    path('delete-notice/<notification_id>/', delete_notification, name="delete-notice"),
]
