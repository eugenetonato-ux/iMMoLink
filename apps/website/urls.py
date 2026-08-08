from django.urls import path
from . import views

app_name = "website"

urlpatterns = [
    path("", views.apropos, name="home"),
    path("a-propos/", views.apropos, name="apropos"),
    path("logements/", views.home, name="logements"),
    path("recherche/", views.recherche, name="recherche"),
    path("annonce/<int:pk>/", views.annonce_detail, name="annonce_detail"),
    path("annonce/<int:pk>/contact/", views.annonce_contact, name="annonce_contact"),
]