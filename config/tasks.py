from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.core.management import call_command

from accounts.models import CustomUser


@shared_task
def clean_up():
    call_command("clearsessions")
    return


@shared_task
def send_invitation_email(email, password):
    domain = settings.SITE_URL
    subject = "Your Spanreed Account is ready to go!"
    msg = (
        f"<p> Your Spanreed account was created successfully! </p>"
        f"<p> You can login to your account using this email and this randomely generated password to manage your subscription. </p>"
        f"<p> Email: {email} </p> <p> Password: {password} </p>"
        f"<p> You can login to your account <a href='{domain}/accounts/login/'> here</a>.</p>"
        f"<p> Once you login, you can change your password to something more memorable via this reset password link. </p>"
        f"<p> {domain}/accounts/password/reset/ </p>"
        f"<p> Thank you, </p>"
        f"<p> The Spanreed team </p>"
    )
    to = email
    email = EmailMessage(
        subject,
        msg,
        settings.DEFAULT_FROM_EMAIL,
        [to],
    )
    email.content_subtype = "html"
    email.send()
    return None


@shared_task
def bill_user(user_pk, payment_method=None, customer=None):
    stripe.api_key = settings.STRIPE_API_KEY
    user = CustomUser.objects.get(pk=user_pk)

    # this will occue when its first set up. We pass the payment method, and customer id from a webhook
    # subsequent billing we use the user's payment method and customer id
    if not payment_method:
        payment_method = user.stripe_payment_method
        customer = user.stripe_cust
    amount = 1999
    try:
        stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            customer=customer,
            payment_method=payment_method,
            off_session=True,
            confirm=True,
        )

        user.emails_left = user.emails_left + 200
        user.plan = "paid"
        user.save()

        # send email to admins
        admin_sub = "An organization just got billed!"
        admin_msg = f"<p> {organization.name} just got billed for ${amount/100}.</p>"
        send_mail(
            admin_sub,
            admin_msg,
            settings.DEFAULT_FROM_EMAIL,
            ["gadly0123@gmail.com"],
            fail_silently=True,
        )
        return True
    except Exception as e:
        # update the user plan to free
        user.plan = "free"
        user.save()
        subject = "Spanreed - Billing failed"
        msg = (
            f"We tried to bill you but failed. Please update your payment information."
            f" or contact us"
            f" Thank you!"
            f" The Spanreed team"
        )
        to = user.email
        send_mail(subject, msg, settings.DEFAULT_FROM_EMAIL, [to], fail_silently=True)
        admin_sub = "A user billing failed!"
        admin_msg = f"<p> {user.email} billing failed. Error: {e} </p>"
        send_mail(
            admin_sub,
            admin_msg,
            settings.DEFAULT_FROM_EMAIL,
            ["gadly0123@gmail.com"],
            fail_silently=True,
        )
        return False
