from django.urls import path

from . import views

urlpatterns = [
    path("gpt/", views.chatbot, name="home"),
]
