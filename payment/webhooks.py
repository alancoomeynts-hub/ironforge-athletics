import stripe
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from membership import services as membership_services
from shop import services as shop_services

from .models import StripeEventLog


@csrf_exempt
def stripe_webhook(request):
    """
    Webhook endpoint for routing Stripe events with
    event log to skip duplicate events
    """

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    # reject requests without a signature.
    if not sig_header:
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WH_SECRET,
        )
    except ValueError:
        # invalid JSON payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # invalid signature
        return HttpResponse(status=400)

    # Map Stripe events to business logic functions
    event_handlers = {
        "checkout.session.completed": handle_checkout_session_completed,
        "invoice.paid": membership_services.renew_membership,
        "customer.subscription.updated": membership_services.update_membership,
        "customer.subcription.deleted": membership_services.cancel_membership,
    }

    handler = event_handlers.get(event.type)

    if handler is None:
        return HttpResponse(status=200)

    # transaction.atomic ensures that all database changes are either committed together or rolled back together
    with transaction.atomic():
        # Log the event and skip duplicate events
        _log, created = StripeEventLog.objects.get_or_create(
            event_id=event.id,
            defaults={"event_type": event.type},
        )
        if not created:
            return HttpResponse(status=200)
        # Process the event and save it to the database
        handler(event.data.object)

    return HttpResponse(status=200)


def handle_checkout_session_completed(session):
    """
    Route a completed Checkout Session to the correct service.

    Shop payments update the order, while subscription checkouts create
    a membership record.
    """

    if session.mode == "payment":
        shop_services.update_order_paid(session)
    elif session.mode == "subscription":
        membership_services.create_membership(session)
    else:
        raise ValueError("Unexpected checkout session mode")
