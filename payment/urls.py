from django.urls import path
from . import views, webhooks

app_name = "payment"

urlpatterns = [
    path("process/", views.payment_process, name="process"),
    path("subscribe/<slug:slug>",views.subscribe, name="subscribe"),
    path("success/", views.payment_success, name="success"),
    path("membership_success/", views.membership_success, name="membership_success"),
    path("canceled/", views.payment_canceled, name="canceled"),
    path("webhook/", webhooks.stripe_webhook, name="stripe-webhook"),
]
