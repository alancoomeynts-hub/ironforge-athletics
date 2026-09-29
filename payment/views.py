from decimal import Decimal
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from shop.models import Order
from membership.models import MembershipType, Membership

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
    #short circuit if user is already a member
    current_membership = Membership.objects.filter(
        user=request.user,
        status__in=[
            Membership.Status.ACTIVE,
            Membership.Status.TRIALING,
            Membership.Status.PAST_DUE,
            Membership.Status.UNPAID,
            Membership.Status.PAUSED,
            Membership.Status.INCOMPLETE,
        ],
    ).first()

    if current_membership:
        messages.error(request, "You are already a member. You can manage your membership from your dashboard.")
        return redirect("user_profile:dashboard")

    # check if user has a previous membership that was canceled
    previous_membership = (
        Membership.objects.filter(
            user=request.user,
            status=Membership.Status.CANCELED,
        )
        .exclude(stripe_customer_id="")
        .first()
    )

    # if user has a previous membership that was canceled, use the stripe customer id from that membership
    customer_details = (
        {"customer": previous_membership.stripe_customer_id}
        if previous_membership
        else {"customer_email": request.user.email}
    )
    membership_type = get_object_or_404(MembershipType, slug=slug, is_available=True)
    stripe.api_key = stripe_secret_key

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {"price": membership_type.stripe_price_id, "quantity": 1},
            ],
            mode="subscription",
            client_reference_id=str(request.user.id),
            metadata={"membership_type_id": str(membership_type.pk)},
            **customer_details,
            success_url=request.build_absolute_uri(reverse("payment:success")),
            cancel_url=request.build_absolute_uri(reverse("payment:canceled")),
        )
    except stripe.error.StripeError as e:
        print(f"Stripe Error: {e}")
        messages.error(request, "An error occurred while processing your payment.")
        return redirect("membership:join")

    return redirect(checkout_session.url, code=303)
