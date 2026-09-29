from datetime import datetime, timezone
from .models import Membership


def create_membership(session):
    """ Create membership record when Subscription checkout session completed and paid"""
    if not session.subscription:
        raise ValueError("Subscription not found")

    if not session.client_reference_id or not session.metadata.membership_type_id:
        raise ValueError("Missing local reference IDs")

    if session.payment_status != "paid":
        raise ValueError("Subscription checkout is not paid")

    Membership.objects.update_or_create(
        stripe_subscription_id=session.subscription,
        defaults={
            "user_id": session.client_reference_id,
            "membership_type_id": session.metadata.membership_type_id,
            "stripe_customer_id": session.customer,
            "stripe_checkout_session_id": session.id,
            "status": Membership.Status.ACTIVE,
        },
    )


def update_membership(invoice):
    """ Update membership when Stripe subscription renewed"""
    if invoice.billing_reason != "subscription_cycle":
        return
    subscription_id = invoice.parent.subscription_details.subscription
    paid_at = invoice.status_transitions.paid_at
    membership = Membership.objects.get(
        stripe_subscription_id=subscription_id,
    )
    membership.last_renewal_date = datetime.fromtimestamp(
        paid_at,
        tz=timezone.utc,
    )  # convert Stripe unix timestamp to datetime
    membership.save()
