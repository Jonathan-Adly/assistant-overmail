from email.utils import parseaddr

import openai
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from markdown import markdown

from overmail.email_utils import (
    send_assistant_email,
    send_help_email,
    send_success_email,
)

from .models import Anon, CustomUser, StripeWebhook


def home(request):
    """Render the home page."""
    return render(request, "home.html")


@csrf_exempt
@require_POST
def add_email(request):
    email = request.POST.get("your-email", "").lower()
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                "price": f"{settings.STRIPE_PRICE_ID}",
                "quantity": 1,
            },
        ],
        mode="payment",
        customer_email=email,
        success_url=settings.SITE_URL + "?success",
        cancel_url=settings.SITE_URL + "?cancel",
    )
    return redirect(checkout_session.url, code=303)


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
        return HttpResponse(status=400)

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
            send_success_email(customer_email)
            return HttpResponse(status=200)
    except Exception as e:
        print(e)
        return HttpResponse(status=400)

    return HttpResponse(status=200)


@csrf_exempt
@require_POST
def email_webhook(request):
    """
    Handles when the server receives an email from the user.
    checks if the email it is sent from is in the database and the user is paid, and has emails left
    if so, decrement the email left, process, and send a response with the result
    if not, response with 200 and drop the email. Letting the user know they need to pay
    """
    from_email = parseaddr(request.POST.get("From"))[1]
    subject = request.POST.get("subject")
    message = request.POST.get("body-plain")

    anon = Anon.objects.filter(email=from_email).first()
    if not anon:
        send_help_email(from_email, reason="email not found")
        return HttpResponse(status=200)
    if not anon.emails_left:
        send_help_email(from_email, reason="no emails left")
        return HttpResponse(status=200)

    # process the email and send a response to anon with the result
    client = settings.OPENAI_CLIENT
    config = settings.DEFAULT_CONFIG
    prompt = """
    You are a helpful assistant that helps people with their emails. 
    You are given a subject and a message with or without user instructions. 
    Do your best with a helpful response. Respond in markdown.\n
    Here is an example: \n
    Subject: "Thank you note" \n
    Message: "Write 2-3 sentences to thank my interviewer, reiterating my excitement for the job opportunity while keeping it cool. Don't make it too formal." \n
    Assistant: Thanks a lot for the great conversation today! I'm genuinely excited about the opportunity to bring my skills to your team and see what we can achieve together. Looking forward to possibly working together! \n
    """
    completion = client.chat.completions.create(
        **config,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Subject: {subject}\nMessage: {message}"},
        ],
    )
    response = completion.choices[0].message.content
    anon.emails_left -= 1
    anon.save()
    send_assistant_email(from_email, response)
    return HttpResponse(status=200)
