from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.core.management import call_command


def send_success_email(email):
    domain = settings.SITE_URL
    site_name = domain.split("//")[-1]
    subject = f"Your {site_name} Account is ready to go!"
    msg = (
        f"<p> Your {site_name} assistant was created successfully! </p>"
        f"<p> You can now email {settings.GPT4_email}using this email and responses will come back. </p>"
        f"<p> If you have any questions, please don't hesitate to ask. Simply respond to this email. </p>"
        f"<p> Thank you, </p>"
        f"<p> The {site_name} team </p>"
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
