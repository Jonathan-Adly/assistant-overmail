from django.contrib import admin

from .models import Anon, CustomUser, StripeWebhook

admin.site.register(CustomUser)
admin.site.register(Anon)
admin.site.register(StripeWebhook)
