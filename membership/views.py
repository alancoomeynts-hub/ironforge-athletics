import stripe
from .models import MembershipType, Membership
from django.shortcuts import render, redirect, reverse
from django.conf import settings

stripe_secret_key = settings.STRIPE_SECRET_KEY


def membership_types(request):
    types = MembershipType.objects.filter(is_available=True)
    current_membership = (
        Membership.objects.filter(
            user=request.user,
            status__in=[
                Membership.Status.ACTIVE,
                Membership.Status.TRIALING,
                Membership.Status.PAST_DUE,
                Membership.Status.UNPAID,
                Membership.Status.PAUSED,
                Membership.Status.INCOMPLETE,
            ],
        )
        .select_related("membership_type")
        .first()
    )
    return render(
        request,
        "membership/join.html",
        {
            "membership_types": types,
            "current_membership": current_membership,
        },
    )


def manage_membership(request):
    membership = Membership.objects.filter(
        user=request.user,
        status=Membership.Status.ACTIVE,
    ).first()

    if membership is None:
        return redirect("membership:join")
    stripe.api_key = stripe_secret_key
    checkout_session = stripe.checkout.Session.retrieve(
        membership.stripe_checkout_session_id
    )

    portal = stripe.billing_portal.Session.create(
        customer=checkout_session.customer,
        return_url=request.build_absolute_uri(
            reverse("membership:join"),
        ),
    )

    return redirect(portal.url, code=303)
