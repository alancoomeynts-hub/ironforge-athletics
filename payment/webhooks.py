import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from shop.models import Order


@csrf_exempt
def stripe_webhook(request):

    print("STRIPE WEBHOOK HIT")

    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WH_SECRET,
        )
    except ValueError as e:
        print("INVALID PAYLOAD:", e)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print("INVALID SIGNATURE:", e)
        return HttpResponse(status=400)

    print("EVENT:", event.type)
    if event.type == "checkout.session.completed":
        session = event.data.object

        if session.mode == "payment":
            try:
                order = Order.objects.get(id=session.client_reference_id)
            except Order.DoesNotExist:
                return HttpResponse(status=404)

            order.status = Order.Status.PAID
            order.stripe_payment_intent_id = session.payment_intent
            order.save()
    return HttpResponse(status=200)
