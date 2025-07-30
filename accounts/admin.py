from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['first_name', 'last_name', 'username', 'is_staff', 'is_active', 'stage']

    fieldsets = UserAdmin.fieldsets + (
        ('Dodatne informacije', {
            'fields': ('phone', 'stage'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Dodatne informacije', {
            'fields': ('phone', 'stage'),
        }),
    )
