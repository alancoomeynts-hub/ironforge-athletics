from .models import Order
import stripe
from django.http import HttpResponse


def update_order_paid(session):
    try:
        order = Order.objects.get(id=session.client_reference_id)
    except Order.DoesNotExist:
        return HttpResponse(status=404)

    if order.status == order.Status.PAID:
        return HttpResponse(status=200)

    payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent, expand=["latest_charge"])
    charge = payment_intent.latest_charge
    receipt_url = charge.receipt_url if charge else None
    order.stripe_receipt_url = receipt_url or ""
    order.status = Order.Status.PAID
    order.stripe_payment_intent_id = session.payment_intent
    order.save()

    return HttpResponse(status=200)