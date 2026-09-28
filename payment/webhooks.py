import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import StripeEventLog
from membership import services as membership_services
from shop import services as shop_services


@csrf_exempt
def stripe_webhook(request):
    """Webhook endpoint for routing Stripe events with event log to skip duplicate events"""

    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WH_SECRET,
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    event_handlers = {
        "checkout.session.completed": handle_checkout_completed,
    }

    handler = event_handlers.get(event.type)
    if handler is None:
        return HttpResponse(status=200)
    with transaction.atomic():
        log, created = StripeEventLog.objects.get_or_create(
            event_id=event.id,
            defaults={"event_type": event.type},
        )
        if not created:
            return HttpResponse(status=200)
        handler(event.data.object)

    return HttpResponse(status=200)


def handle_checkout_completed(session):
    if session.mode == "payment":
        shop_services.update_order_paid(session)
    elif session.mode == "subscription":
        membership_services.create_membership(session)
    else:
        raise ValueError("Unexpected checkout session mode")
