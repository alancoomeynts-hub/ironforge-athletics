from decimal import Decimal
import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from shop.cart import Cart
from shop.models import Order


stripe_secret_key = settings.STRIPE_SECRET_KEY


def payment_process(request):
    order_id = request.session.get("order_id")
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        line_items = []
        for item in order.items.all():
            line_items.append(
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {
                            "name": str(item.product.name),
                        },
                        "unit_amount": int(
                            Decimal(str(item.line_total)) * Decimal("100")
                        ),
                    },
                    "quantity": int(item.quantity),
                }
            )

        if order.shipping_method == "delivery":
            line_items.append(
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {
                            "name": "Delivery",
                        },
                        "unit_amount": int(
                            Decimal(str(order.shipping_cost)) * Decimal("100")
                        ),
                    },
                    "quantity": 1,
                }
            )

        session_data = {
            "mode": "payment",
            "payment_method_types": ["card"],
            "client_reference_id": str(order.id),
            "success_url": request.build_absolute_uri(reverse("payment:success")),
            "cancel_url": request.build_absolute_uri(reverse("payment:canceled")),
            "line_items": line_items,
        }

        stripe.api_key = stripe_secret_key

        session = stripe.checkout.Session.create(**session_data)
        return redirect(
            session.url,
            code=303,
        )
    else:
        return render(
            request,
            "payment/process.html",
            locals(),
        )


def payment_success(request):
    cart = Cart(request)
    cart.clear()
    return render(request, "payment/success.html")


def payment_canceled(request):
    return render(request, "payment/canceled.html")
