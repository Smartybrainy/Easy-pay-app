from .forms import CustomUserCreationForm, CustomChangeForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib import admin
User = get_user_model()

from .models import Profile, Notification

def make_user_is_active_false(ModelAdmin, request, queryset):
    queryset.update(is_active=False)
make_user_is_active_false.short_description = "set is_active to False"


def make_user_is_active_true(ModelAdmin, request, queryset):
    queryset.update(is_active=True)
make_user_is_active_true.short_description = 'set is_active to True'


class CustomUserAdmin(BaseUserAdmin):

    add_form = CustomUserCreationForm
    form = CustomChangeForm
    model = User
    list_display = (
                    'unique_tag',
                    'email',
                    'date_joined',
                    'phone_number_verified',
                    'phone_number',
                    'country_code',
                    'two_factor_auth',
                    'is_staff',
                    'is_active',
                    )
    list_filter = (
                    'unique_tag',
                    'email',
                    'date_joined',
                    'phone_number_verified',
                    'phone_number',
                    'country_code',
                    'two_factor_auth',
                    'is_staff',
                    'is_active'
                    )
    fieldsets = (
        (None, {'fields': ('password', 'unique_tag', 'email')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
        ('OTP', {'fields': (
                    'full_name',
                    'phone_number_verified',
                    'phone_number',
                    'country_code',
                    'two_factor_auth'
                    )
                 })
    )
    add_fieldsets = (
        ('Add New User', {
            'classes': ('wide',),
            'fields': (
                'phone_number',
                'unique_tag',
                'email',
                'password1',
                'password2',
                'is_staff',
                'is_active'
                )
        }
        ),
        ('OTP', {'fields': (
                    'full_name',
                    'phone_number_verified',
                    'country_code',
                    'two_factor_auth'
                    )
                 })
    )
    search_fields = ('unique_tag', 'email')
    ordering = ('unique_tag',)
    actions = [make_user_is_active_false, make_user_is_active_true]

    # def get_inline_instances(self, request, obj=None):
    #     if not obj:
    #         return list()
    #     return super(CustomUserAdmin, self).get_inline_instances(request, obj)

@admin.register(Notification)
class AdminNotification(admin.ModelAdmin):
    list_display = (
        'user',
        'title',
        'viewed',
        'date_created'
)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile)

