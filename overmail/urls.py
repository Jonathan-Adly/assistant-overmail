from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("add-email/", views.add_email, name="add_email"),
    path("stripe-webhook/", views.stripe_webhook, name="stripe_webhook"),
    path("opennode-webhook/", views.opennode_webhook, name="opennode_webhook"),
    path("email-webhook/", views.email_webhook, name="email_webhook"),
]
