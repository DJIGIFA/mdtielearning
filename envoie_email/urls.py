from django.urls import path

from .views import envoie_email

urlpatterns = [
    path("send", envoie_email, name="envoie_email")
]