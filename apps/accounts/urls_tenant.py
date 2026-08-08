from django.urls import path

from apps.favorites import views as favorites_views

from . import views

app_name = "tenant"

urlpatterns = [
    path("", views.tenant_dashboard, name="tenant_dashboard"),
    path("favoris/", favorites_views.mes_favoris, name="favoris"),
]
