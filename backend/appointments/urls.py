from django.urls import path

from . import views
from .zalo_webhook import webhook

urlpatterns = [
    path("health/", views.health, name="health"),
    path("zalo-miniapp/webhook/", webhook, name="zalo-miniapp-webhook"),
    path("specialties/", views.specialties, name="specialties"),
    path("appointments/", views.create_appointment, name="create-appointment"),
]
