from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    ordering = ('email', 'is_dj')

    list_display = ('email', 'is_dj','is_staff', 'is_active')

    # Update the fields used in the user creation form in the admin site
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_dj', 'is_staff', 'is_active')}
        ),
    )
    
    # Update the fields used in the user change form in the admin site
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (('Permissions'), {'fields': ('is_dj', 'is_staff', 'is_active')}),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set()

        if not is_superuser:
            disabled_fields |= {
                'is_superuser',
                'user_permissions',
            }

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True

        return form

# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)
