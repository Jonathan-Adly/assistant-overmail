import json

import requests
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from svix.webhooks import Webhook, WebhookVerificationError

from config.tasks import send_success_email

from .models import AlbyWebhook, Anon, CustomUser, EmailWebhook, StripeWebhook


def home(request):
    """Home page.
    On POST save email in session and start payment process.
    On GET render home home with conditional message if this is a redirect from a successful payment.
    """
    if request.method == "POST":
        email = request.POST.get("email", "").lower()
        if email:
            request.session["email"] = email
            return render(request, "accounts/payment.html", {"email": email})
        else:
            message = "Please enter a valid email address."
            messages.error(request, message)
            return render(request, "overmail/home.html")

    session_id = request.GET.get("session_id", "")
    if session_id:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)
        if session.status == "complete":
            message = "Thank you for your payment. You will receive a welcome email confirming your details."
            messages.success(request, message)
        else:
            print(session)
            message = "Something went wrong. Please try again."
            messages.error(request, message)
    return render(request, "overmail/home.html")


def stripe_checkout(request):
    """Create a Stripe checkout session and return the client secret to the frontend."""
    email = request.session.get("email").lower()
    if not email:
        message = "Please enter a valid email address."
        messages.error(request, message)
        return render(request, "accounts/home.html")

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        checkout_session = stripe.checkout.Session.create(
            ui_mode="embedded",
            line_items=[
                {
                    "price": f"{settings.STRIPE_PRICE_ID}",
                    "quantity": 1,
                },
            ],
            mode="payment",
            customer_email=email,
            return_url=settings.SITE_URL + "?session_id={CHECKOUT_SESSION_ID}",
        )
        client_secret = checkout_session.client_secret
        public_key = settings.STRIPE_PUBLIC_KEY
        return render(
            request,
            "accounts/stripe-checkout.html",
            {"stripe_public_key": public_key, "client_secret": client_secret},
        )
    except Exception as e:
        print(e)
        message = "Something went wrong. Please try again."
        return HttpResponse(message)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhooks."""
    webhook_secret = settings.STRIPE_WH_SECRET
    signature = request.headers.get("stripe-signature")
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        event = stripe.Webhook.construct_event(
            payload=request.body, sig_header=signature, secret=webhook_secret
        )
    except Exception as e:
        print(e)

    event_type = event["type"]
    data_object = event["data"]["object"]
    event_id = event["id"]
    try:
        if event_type == "checkout.session.completed":
            customer_email = data_object["customer_details"]["email"]
            anon, created = Anon.objects.get_or_create(email=customer_email)
            anon.emails_left += 200
            anon.save()
            stripe_webhook = StripeWebhook.objects.create(
                event_id=event_id, event_type=event_type
            )
    except Exception as e:
        print(e)

    return HttpResponse(status=200)


@csrf_exempt
@require_POST
def alby_webhook(request):
    """Handle Alby webhooks."""
    headers = request.headers
    payload = request.body
    try:
        wh = Webhook(settings.ALBY_WH_SECRET)
        msg = wh.verify(payload, headers)
        payload = json.loads(request.body)
        if not payload["payer_email"]:
            return HttpResponse(status=200)
        fiat_in_cents = int(payload["fiat_in_cents"])
        # should be around $20 USD
        if not 1900 < fiat_in_cents < 2100:
            return HttpResponse(status=200)
        alby_payment = AlbyWebhook.objects.create(payload=payload)
        anon, created = Anon.objects.get_or_create(
            email=alby_payment.payload["payer_email"]
        )
        anon.emails_left += 200
        anon.save()
        return HttpResponse(status=200)
    except json.JSONDecodeError or WebhookVerificationError:
        print(request.body)
        return HttpResponse(status=400)


@csrf_exempt
@require_POST
def email_webhook(request):
    # check if the email it is sent from is in the database and the user is paid, and has emails left
    # if so, decrement the email left and response back "got yoru email"
    # if not, response with 200 and drop the email
    # email = request.POST.get("from").split("<")[1].split(">")[0].strip()
    # subject = request.POST.get("subject")
    # message = request.POST.get("body-html")
    try:
        payload = json.loads(request.body)
        EmailWebhook.objects.create(payload=payload)
        return HttpResponse(status=200)
    except json.JSONDecodeError:
        print(request.body)
        return HttpResponse(status=400)


def about(request):
    return render(request, "overmail/about.html")


def pricing(request):
    return render(request, "overmail/pricing.html")


def tos(request):
    return render(request, "overmail/tos.html")
