from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Plans(models.TextChoices):
        FREE = "free", "Free"
        PAID = "paid", "Paid"

    plan = models.CharField(max_length=10, choices=Plans.choices, default=Plans.FREE)
    stripe_cust = models.CharField(max_length=250, blank=True)
    stripe_payment_method = models.CharField(max_length=250, blank=True)
    email_count = models.SmallIntegerField(default=0)
    subscribe_to_emails = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["email"], name="unique_email")]
