import stripe
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from config.tasks import bill_user, send_invitation_email

from .models import CustomUser


def home(request):
    return render(request, "accounts/home.html")


@require_POST
def create_account(request):
    email = request.POST.get("email")
    random_password = get_random_string(length=10)
    user_name = email.split("@")[0] + get_random_string(length=3)
    try:
        user = CustomUser.objects.create_user(
            username=user_name, email=email, password=random_password
        )
    except Exception as e:
        return HttpResponse(str(e))

    send_invitation_email(email, random_password)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="setup",
        ui_mode="embedded",
        return_url=f"{settings.SITE_URL}/"
        + "?session_id={CHECKOUT_SESSION_ID}",  # change
        client_reference_id=user.pk,
    )
    client_secret = session.client_secret
    return render(
        request,
        "accounts/stripe_pricing_table.html",
        {
            "client_secret": client_secret,
            "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
        },
    )


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
    if event_type == "checkout.session.completed":
        print(data_object)
        # get client_reference_id
        user_id = int(data_object["client_reference_id"])

        # wrap this in try except when we finish development
        user = CustomUser.objects.get(pk=user_id)
        # charge for 200 emails
        setup_intent = stripe.SetupIntent.retrieve(data_object["setup_intent"])
        payment_method = stripe.PaymentMethod.retrieve(setup_intent["payment_method"])

        # bill the user and change their plan
        billed = bill_user(
            user_pk=user.pk,
            payment_method=payment_method["id"],
            customer=data_object["customer"],
        )
        if not billed:
            return HttpResponse(status=200)

        # only update the user if billing was successful, save their info for future billing
        user.stripe_cust = data_object["customer"]
        user.payment_method = payment_method["id"]
        user.save()
    return HttpResponse(status=200)


@csrf_exempt
@require_POST
def email_received_webhook(request):
    # check if the email it is sent from is in the database and the user is paid, and has emails left
    # if so, decrement the email left and response back "got yoru email"
    # if not, response with 200 and drop the email
    email = request.POST.get("from").split("<")[1].split(">")[0].strip()
    subject = request.POST.get("subject")
    message = request.POST.get("body-html")
    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return HttpResponse(status=200)
    if user.plan == "free":
        return HttpResponse(status=200)
    if user.email_count <= 0:
        billed = bill_user(user.pk)
        if not billed:
            return HttpResponse(status=200)
    user.email_count = user.email_count - 1
    user.save()
    return HttpResponse("Got your email")
