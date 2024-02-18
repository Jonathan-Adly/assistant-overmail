from django.conf import settings


def llm_email(request):
    return {"GPT4_EMAIL": settings.GPT4_EMAIL}
