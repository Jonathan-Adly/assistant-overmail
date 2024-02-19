import json
from email.utils import parseaddr

import requests
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.http import HttpResponse
from django.shortcuts import render
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
            return render(request, "overmail/payment.html", {"email": email})
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
        return render(request, "overmail/home.html")

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
            "overmail/stripe-checkout.html",
            {"stripe_public_key": public_key, "client_secret": client_secret},
        )
    except Exception as e:
        print(e)
        message = "Something went wrong. Please try again."
        return HttpResponse(message)


def alby_checkout(request):
    # goal is to create a lighting invoice and return the payment request with QR code to the frontend
    # first we will get the current price of bitcoin
    email = request.session.get("email")
    if not email:
        message = "Please enter a valid email address."
        messages.error(request, message)
        return render(request, "overmail/home.html")
    bitcoin_price_api = "https://api.kraken.com/0/public/Trades?pair=XBTUSD&count=1"
    bitcoin_price_usd = float(
        requests.get(bitcoin_price_api).json()["result"]["XXBTZUSD"][0][0]
    )
    satoshis = int((20 / bitcoin_price_usd) * 100_000_000)
    # then we will create a lightning invoice
    albi_api = "https://api.getalby.com/invoices"
    payload = {
        "amount": satoshis,
        "description": "200 emails of AI Assistant overmail",
        "payer_email": email,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.ALBY_API_KEY}",
    }
    response = requests.post(albi_api, headers=headers, json=payload)
    invoice = response.json()
    qr_code = invoice["qr_code_svg"]
    payment_request = invoice["payment_request"]
    return render(
        request,
        "overmail/alby-checkout.html",
        {
            "qr_code": qr_code,
            "payment_request": payment_request,
            "bitcoin_price_usd": bitcoin_price_usd,
            "sats": satoshis,
        },
    )


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
    """checks if the email it is sent from is in the database and the user is paid, and has emails left
    if so, decrement the email left, process, and send a response with the result
    if not, response with 200 and drop the email. Letting the user know they need to pay
    """
    from_email = parseaddr(request.POST.get("from"))[1]
    subject = request.POST.get("subject")
    message = request.POST.get("body-plain")
    print(from_email, subject, message)
    anon = Anon.objects.filter(email=from_email).first()
    if not anon:
        # send email to anon, telling them to pay
        print("anon not found")
        # TODO
        return HttpResponse(status=200)
    if not anon.emails_left:
        # TODO
        # send email to anon, telling them to pay
        print("no emails left")
        return HttpResponse(status=200)

    # process the email and send a response to anon with the result
    anon.emails_left -= 1
    anon.save()
    # TODO
    return HttpResponse(status=200)


def about(request):
    return render(request, "overmail/about.html")


def pricing(request):
    return render(request, "overmail/pricing.html")


def tos(request):
    return render(request, "overmail/tos.html")
