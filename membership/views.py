import stripe
from django.conf import settings
from django.shortcuts import redirect, render, reverse

from user_profile.decorators import staff_or_membership_required

from .models import Membership, MembershipType

stripe_secret_key = settings.STRIPE_SECRET_KEY


def membership_types(request):
    """
        render membership types and join buttons.
        If the user is a member, show a button to the manage portal
    """

    types = MembershipType.objects.filter(is_available=True)

    # check if a logged-in user has active membership.
    # Flag used in template to show the join buttons or manage portal
    current_membership = None
    if request.user.is_authenticated:
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


@staff_or_membership_required
def manage_membership(request):
    """Redirect to Stripe billing portal"""

    membership = Membership.objects.filter(
        user=request.user,
        status=Membership.Status.ACTIVE,
    ).first()

    # if user is not a member, redirect to join page
    if membership is None:
        return redirect("membership:join")
    stripe.api_key = stripe_secret_key
    checkout_session = stripe.checkout.Session.retrieve(
        membership.stripe_checkout_session_id
    )

    # Redirect to Stripe billing portal
    portal = stripe.billing_portal.Session.create(
        customer=checkout_session.customer,
        return_url=request.build_absolute_uri(
            reverse("membership:join"),
        ),
    )

    return redirect(portal.url, code=303)
