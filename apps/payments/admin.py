from django.contrib import admin

from .models import ContactUnlock, Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("reference", "locataire", "annonce", "montant", "methode", "statut", "created_at")
    list_filter = ("statut", "methode")
    search_fields = ("reference", "locataire__email", "annonce__titre")
    readonly_fields = ("reference",)


@admin.register(ContactUnlock)
class ContactUnlockAdmin(admin.ModelAdmin):
    list_display = ("locataire", "annonce", "unlocked_at")
    search_fields = ("locataire__email", "annonce__titre")
