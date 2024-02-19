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
    event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=255)
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event_id

    def retrieve_from_stripe(self, event_id):
        "why save the JSON if stripe has it?"
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_response = stripe.Event.retrieve(event_id)
        return str(stripe_response)


class AlbyWebhook(models.Model):
    # json field
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)


class EmailWebhook(models.Model):
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)
