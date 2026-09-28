from .models import Membership

def create_membership(session):
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

