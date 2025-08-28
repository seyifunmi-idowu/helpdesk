from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserInstance


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'firstName', 'lastName', 'isEnabled', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'isEnabled']
    search_fields = ['email', 'firstName', 'lastName']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('firstName', 'lastName', 'proxyId', 'timezone', 'timeformat')}),
        (_('Permissions'), {'fields': ('is_staff', 'isEnabled', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'lastOtpGeneratedAt')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'firstName', 'password1', 'password2', 'is_staff', 'isEnabled', 'is_superuser'),
        }),
    )


@admin.register(UserInstance)
class UserInstanceAdmin(admin.ModelAdmin):
    list_display = ['user', 'source', 'isActive', 'isVerified', 'createdAt']
    list_filter = ['isActive', 'isVerified', 'isStarred']
    search_fields = ['user__email', 'source', 'contactNumber', 'designation']


# Register custom User
admin.site.register(User, UserAdmin)
