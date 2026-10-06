from django.urls import path
from . import views

urlpatterns = [
    path("config/", views.chatbot_config_api, name="chatbot_config"),
    path("chat/", views.chatbot_chat_api, name="chatbot_chat"),
    path("feedback/", views.chatbot_feedback_api, name="chatbot_feedback"),
]
