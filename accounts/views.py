import stripe
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from config.tasks import bill_user, send_invitation_email

from .models import AlbyWebhook, Anon, CustomUser, EmailWebhook, StripeWebhook


def home(request):
    return render(request, "accounts/home.html")


@csrf_exempt
@require_POST
def stripe_webhook(request):
    webhook_secret = settings.WEBHOOK_SECRET
    if settings.DEBUG:
        webhook_secret = (
            "whsec_96e16cf2eda14bc3513af72b38eea872a29c6a1324ed4fbf27d863e39a024515"
        )
    signature = request.headers.get("stripe-signature")
    stripe.api_key = settings.STRIPE_API_KEY
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
        stripe_webhook = StripeWebhook.objects.create(
            event_id=event_id, event_type=event_type
        )
    except Exception as e:
        print(e)
    return HttpResponse(status=200)


@csrf_exempt
@require_POST
def alby_webhook(request):
    try:
        payload = json.loads(request.body)
        AlbyWebhook.objects.create(payload=payload)
        return HttpResponse(status=200)
    except json.JSONDecodeError:
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
