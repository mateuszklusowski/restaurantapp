from django.contrib import admin
from django.apps import apps
from django.utils.translation import gettext as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


class UserAdmin(BaseUserAdmin):
    ordering = ('id',)
    list_display = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2')
        }),
    )


admin.site.register(User, UserAdmin)

for model in apps.get_models():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        continue
