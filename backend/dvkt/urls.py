from django.urls import path
from .views import service_prices

urlpatterns = [path("", service_prices, name="dvkt-prices")]
