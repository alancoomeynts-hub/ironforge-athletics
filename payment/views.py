from decimal import Decimal
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from shop.cart import Cart
from shop.models import Order
from membership.models import MembershipType


stripe_secret_key = settings.STRIPE_SECRET_KEY

@login_required
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
            "customer_email": order.email,
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
    return render(request, "payment/success.html")


def payment_canceled(request):
    return render(request, "payment/canceled.html")


@login_required
def subscribe(request, slug):
    membership_type = get_object_or_404(MembershipType, slug=slug, is_available=True)
    stripe.api_key = stripe_secret_key

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {'price': membership_type.stripe_price_id, 'quantity': 1},
            ],
            mode='subscription',
            client_reference_id=str(request.user.id),
            metadata={'membership_type_id': str(membership_type.pk)},
            customer_email=request.user.email,
            success_url=request.build_absolute_uri(reverse('payment:success')),
            cancel_url=request.build_absolute_uri(reverse('payment:canceled')),

        )
    except stripe.error.StripeError as e:
        messages.error(request, 'An error occurred while processing your payment.')
        return redirect("membership:join")

    return redirect(checkout_session.url, code=303)

