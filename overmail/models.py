import stripe
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Only for super users"""

    class Meta:
        constraints = [models.UniqueConstraint(fields=["email"], name="unique_email")]


class Anon(models.Model):
    email = models.EmailField(unique=True)
    emails_left = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)


class StripeWebhook(models.Model):
    event_id = models.CharField(max_length=255)
    event_type = models.CharField(max_length=255)
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event_id

    def retrieve_from_stripe(self, event_id):
        "why save the JSON if stripe has it?"
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_response = stripe.Event.retrieve(event_id)
        return str(stripe_response)


class OpenNodeWebhook(models.Model):
    charge_id = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    description = models.TextField()
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.charge_id
