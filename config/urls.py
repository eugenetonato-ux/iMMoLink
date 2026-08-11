from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from decouple import config

ADMIN_URL_PATH = config("ADMIN_URL_PATH", default="cpanel_administrateur")

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("compte/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.api.urls")),
    path("", include("apps.website.urls")),
    path("espace-locataire/", include("apps.accounts.urls_tenant")),
    path("espace-proprietaire/", include("apps.accounts.urls_owner")),
    path("paiement/", include("apps.payments.urls")),
    path("localisation/", include("apps.locations.urls")),
    path("favoris/", include("apps.favorites.urls")),
    path(f"{ADMIN_URL_PATH}/", include("apps.adminpanel.urls")),
    path("geo/", include("apps.geo.urls", namespace="geo")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)