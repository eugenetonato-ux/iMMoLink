from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import OwnerProfile, TenantProfile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "username", "role", "is_active", "is_staff", "date_joined")
    list_filter = ("role", "is_active")
    search_fields = ("email", "username", "first_name", "last_name")
    fieldsets = UserAdmin.fieldsets + (
        ("iMMoLink", {"fields": ("role", "photo")}),
    )


@admin.register(OwnerProfile)
class OwnerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "commune", "quartier", "whatsapp", "verifie")
    list_filter = ("verifie", "commune")
    search_fields = ("user__email", "whatsapp")


@admin.register(TenantProfile)
class TenantProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "ville", "quartier")
    search_fields = ("user__email",)