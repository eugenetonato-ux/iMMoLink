from django.contrib import admin

from .models import PlatformSettings


@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    list_display = ("frais_contact", "devise", "moov_money_actif", "mtn_money_actif", "updated_at")

    def has_add_permission(self, request):
        # Singleton : on ne peut pas en créer un second depuis le django-admin.
        return not PlatformSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
