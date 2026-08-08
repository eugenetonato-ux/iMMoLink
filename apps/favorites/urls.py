from django.urls import path

from . import views

app_name = "favorites"

urlpatterns = [
    path("toggle/<int:annonce_id>/", views.toggle_favorite, name="toggle"),
]
