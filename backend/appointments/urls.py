from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health, name="health"),
    path("specialties/", views.specialties, name="specialties"),
    path("appointments/", views.create_appointment, name="create-appointment"),
]
