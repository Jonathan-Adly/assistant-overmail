from django.conf import settings
from django.core.mail import EmailMessage


def send_success_email(email):
    domain = settings.SITE_URL
    site_name = domain.split("//")[-1]
    subject = f"Your {site_name} Assistant is ready to go!"
    msg = (
        f"<p> Your {site_name} assistant was created successfully. You now have 200 emails! </p>"
        f"<p> You can now email {settings.GPT4_EMAIL} using this email and responses will come back. </p>"
        f"<p> For example, forward a colleage email with instruction craft an appropriate response"
        "or a customer email giving the model additional instruction. GPT-4 is pretty smart, "
        "and can figure out the task with minimal directions. </p>"
        f"<p> If you run out of emails, visit {domain}, enter your email, and pay for more. </p>"
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


def send_help_email(email, reason=None):
    reason_map = {
        "email not found": "We couldn't find your email in our system. Please sign up for an account.",
        "no emails left": "You have no emails left. Please sign up for a plan.",
    }
    domain = settings.SITE_URL
    site_name = domain.split("//")[-1]
    subject = f"Your {site_name} Assistant needs your attention"
    msg = (
        f"<p> Your {site_name} assistant needs your attention. </p>"
        f"<p> {reason_map[reason]} </p>"
        f"<p> To add your email to our system or add more emails, visit {domain}, enter your email, and add your payment information. </p>"
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


def send_assistant_email(email, response, subject, message):
    domain = settings.SITE_URL
    site_name = domain.split("//")[-1]
    subject = f"RE: {subject}"
    msg = (
        f"<p> Your {site_name} assistant has a response for you. Response: </p> <hr>"
        f"<p> Your message: subject: {subject} <br> Message: {message} </p>"
        f"<p> Assistant: {response} </p>"
        f"<hr>"
        f"<p> If you have any questions, please don't hesitate to ask. Email us at {settings.DEFAULT_FROM_EMAIL}. </p>"
        f"<p> Thank you, </p>"
        f"<p> The {site_name} team </p>"
    )
    to = email
    email = EmailMessage(
        subject,
        msg,
        settings.GPT4_EMAIL,
        [to],
    )
    email.content_subtype = "html"
    email.send()
    return None
