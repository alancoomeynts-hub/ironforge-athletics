from decimal import Decimal

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from membership.models import Membership, MembershipType
from shop.models import Order

# Stripe secret key loaded from environment variables via Django settings.
stripe_secret_key = settings.STRIPE_SECRET_KEY


@login_required
def payment_process(request):
    """
    Start the Stripe Checkout payment process for an existing order.

    The order ID is stored in the session after the checkout form is
    completed. On a GET request, this view displays a payment summary page.
    On a POST request, it creates a Stripe Checkout Session and redirects
    the customer to Stripe's hosted payment page.
    """

    # Retrieve the order ID stored in the user's session.
    # If it is missing or invalid, return a 404 page.
    order_id = request.session.get("order_id")
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        # Build the list of items Stripe should charge for.
        line_items = []

        # Convert each order item into the format required by Stripe.
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

        # Add delivery as a separate line item if the customer chose delivery.
        if order.shipping_method == "delivery":
            line_items.append(
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {
                            "name": "Delivery",
                        },
                        # Convert the delivery cost from euros to cents.
                        "unit_amount": int(
                            Decimal(str(order.shipping_cost)) * Decimal("100")
                        ),
                    },
                    "quantity": 1,
                }
            )

        # Data sent to Stripe when creating the Checkout Session.
        session_data = {
            "mode": "payment",
            "payment_method_types": ["card"],
            "client_reference_id": str(order.id),
            "success_url": request.build_absolute_uri(reverse("payment:success")),
            "cancel_url": request.build_absolute_uri(reverse("payment:canceled")),
            "line_items": line_items,
            "customer_email": order.email,
        }

        # Set the API key for this Stripe request.
        stripe.api_key = stripe_secret_key

        # Ask Stripe to create a hosted Checkout Session.
        session = stripe.checkout.Session.create(**session_data)

        # Send the customer to Stripe's secure payment page.
        # HTTP 303 tells the browser to use GET when following the redirect.
        return redirect(
            session.url,
            code=303,
        )
    else:
        # Display the payment summary page before the customer proceeds.
        return render(
            request,
            "payment/process.html",
            locals(),
        )


def payment_success(request):
    """
    Display the page shown after a customer completes a shop payment.
    """

    return render(request, "payment/success.html")


def payment_canceled(request):
    """
    Display the page shown if a customer cancels Stripe Checkout.
    """

    return render(request, "payment/canceled.html")


@login_required
def subscribe(request, slug):
    """
    Start a Stripe Checkout subscription for the selected membership type.

    The membership type is identified by its slug. The view prevents users
    with an existing membership from subscribing again and reuses a previous
    Stripe customer ID where possible.
    """

    # Short-circuit if the user already has a membership that is not canceled.
    # This prevents duplicate subscriptions.
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
        messages.error(
            request,
            "You are already a member. You can manage your membership from your dashboard.",
        )
        return redirect("user_profile:dashboard")

    # Check whether the user previously had a membership that was canceled.
    previous_membership = (
        Membership.objects.filter(
            user=request.user,
            status=Membership.Status.CANCELED,
        )
        .exclude(stripe_customer_id="")
        .first()
    )

    # If the user has a previous canceled membership, reuse its Stripe
    # customer ID. Otherwise, pass their email address so Stripe can create or match
    # a customer during checkout.
    customer_details = (
        {"customer": previous_membership.stripe_customer_id}
        if previous_membership
        else {"customer_email": request.user.email}
    )

    membership_type = get_object_or_404(MembershipType, slug=slug, is_available=True)

    stripe.api_key = stripe_secret_key

    try:
        # Create a Stripe Checkout Session in subscription mode.
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {"price": membership_type.stripe_price_id, "quantity": 1},
            ],
            mode="subscription",
            client_reference_id=str(request.user.id),
            metadata={"membership_type_id": str(membership_type.pk)},
            **customer_details,
            success_url=request.build_absolute_uri(
                reverse("payment:membership_success")
            ),
            cancel_url=request.build_absolute_uri(reverse("payment:canceled")),
        )
    except stripe.error.StripeError as e:
        print(f"Stripe Error: {e}")
        messages.error(request, "An error occurred while processing your payment.")
        return redirect("membership:join")

    # Send the customer to Stripe's hosted subscription checkout page.
    return redirect(checkout_session.url, code=303)


def membership_success(request):
    """
    Display the page shown after a customer starts a membership subscription.
    """

    return render(request, "payment/membership_success.html")
