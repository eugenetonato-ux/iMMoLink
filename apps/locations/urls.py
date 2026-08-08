from django.urls import path

from . import views

app_name = "locations"

urlpatterns = [
    path("quartiers/<int:ville_id>/", views.quartiers_par_ville, name="quartiers_par_ville"),
]
