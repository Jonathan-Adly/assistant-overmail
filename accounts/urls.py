from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("pricing/", views.pricing, name="pricing"),
    path("stripe-webhook/", views.stripe_webhook, name="stripe_webhook"),
    path("alby-webhook/", views.alby_webhook, name="alby_webhook"),
    path("email-webhook/", views.email_webhook, name="email_webhook"),
]
