from datetime import date, datetime, timezone
from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from membership.models import Membership, MembershipType
from membership.services import (
    cancel_membership,
    create_membership,
    renew_membership,
    update_membership,
)

User = get_user_model()


class TestCreateMembership(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass",
        )
        self.membership_type = MembershipType.objects.create(
            name="Standard",
            slug="standard",
            price=100,
            stripe_product_id="prod_123",
            stripe_price_id="price_123",
            is_available=True,
        )

    def test_happy_path(self):
        """Test that a new membership is created correctly."""
        session = Mock()
        session.subscription = "sub_123"
        session.client_reference_id = self.user.id
        session.metadata = Mock()
        session.metadata.membership_type_id = self.membership_type.id
        session.payment_status = "paid"
        session.customer = "cus_123"
        session.id = "cs_123"

        create_membership(session)

        membership = Membership.objects.get(stripe_subscription_id="sub_123")
        self.assertEqual(membership.user, self.user)
        self.assertEqual(membership.membership_type, self.membership_type)
        self.assertEqual(membership.status, Membership.Status.ACTIVE)
        self.assertEqual(membership.stripe_customer_id, "cus_123")
        self.assertEqual(membership.stripe_checkout_session_id, "cs_123")

    def test_raises_if_client_reference_id_missing(self):
        """Test that an error is raised if client_reference_id is missing."""
        session = Mock()
        session.subscription = "sub_123"
        session.client_reference_id = None
        session.metadata = Mock()
        session.metadata.membership_type_id = self.membership_type.id
        session.payment_status = "paid"

        with self.assertRaises(ValueError):
            create_membership(session)

    def test_raises_if_membership_type_id_missing(self):
        """Test that an error is raised if membership_type_id is missing."""
        session = Mock()
        session.subscription = "sub_123"
        session.client_reference_id = self.user.id
        session.metadata = Mock()
        session.metadata.membership_type_id = None
        session.payment_status = "paid"

        with self.assertRaises(ValueError):
            create_membership(session)

    def test_raises_if_not_paid(self):
        """Test that an error is raised if the subscription is not paid."""
        session = Mock()
        session.subscription = "sub_123"
        session.client_reference_id = self.user.id
        session.metadata = Mock()
        session.metadata.membership_type_id = self.membership_type.id
        session.payment_status = "unpaid"

        with self.assertRaises(ValueError):
            create_membership(session)


class TestRenewMembership(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            password="testpass",
        )
        self.membership_type = MembershipType.objects.create(
            name="Standard",
            slug="standard",
            price=100,
            stripe_product_id="prod_123",
            stripe_price_id="price_123",
            is_available=True,
        )

    def test_happy_path_renews_membership(self):
        """Test that a membership is renewed correctly."""
        membership = Membership.objects.create(
            user=self.user,
            membership_type=self.membership_type,
            stripe_subscription_id="sub_123",
            status=Membership.Status.ACTIVE,
        )

        paid_at_ts = int(datetime(2026, 10, 1, tzinfo=timezone.utc).timestamp())
        invoice = Mock()
        invoice.billing_reason = "subscription_cycle"
        invoice.parent = Mock()
        invoice.parent.subscription_details = Mock()
        invoice.parent.subscription_details.subscription = "sub_123"
        invoice.status_transitions = Mock()
        invoice.status_transitions.paid_at = paid_at_ts

        renew_membership(invoice)

        membership.refresh_from_db()
        expected_date = datetime(2026, 10, 1, tzinfo=timezone.utc).date()
        self.assertEqual(membership.last_renewal_date, expected_date)

    def test_ignores_non_cycle_invoice(self):
        """Test that an invoice with a billing reason other than "subscription_cycle" is ignored."""
        membership = Membership.objects.create(
            user=self.user,
            membership_type=self.membership_type,
            stripe_subscription_id="sub_123",
            status=Membership.Status.ACTIVE,
            last_renewal_date=datetime(2020, 1, 1, tzinfo=timezone.utc),
        )

        invoice = Mock()
        invoice.billing_reason = "subscription_create"
        invoice.parent = Mock()
        invoice.parent.subscription_details = Mock()
        invoice.parent.subscription_details.subscription = "sub_123"

        renew_membership(invoice)

        membership.refresh_from_db()
        self.assertEqual(membership.last_renewal_date, date(2020, 1, 1))


class TestUpdateMembership(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser3",
            email="test3@example.com",
            password="testpass",
        )
        self.membership_type = MembershipType.objects.create(
            name="Standard",
            slug="standard",
            price=100,
            stripe_product_id="prod_123",
            stripe_price_id="price_123",
            is_available=True,
        )

    def test_happy_path_updates_status_and_type(self):
        """Test that a membership is updated correctly."""
        membership = Membership.objects.create(
            user=self.user,
            membership_type=self.membership_type,
            stripe_subscription_id="sub_123",
            status=Membership.Status.ACTIVE,
        )

        new_price_id = "price_new"
        new_type = MembershipType.objects.create(
            name="Premium",
            slug="premium",
            price=200,
            stripe_product_id="prod_premium",
            stripe_price_id=new_price_id,
            is_available=True,
        )

        subscription = Mock()
        subscription.id = "sub_123"
        subscription.status = "past_due"
        subscription.items = Mock()
        subscription.items.data = [Mock()]
        subscription.items.data[0].price = Mock()
        subscription.items.data[0].price.id = new_price_id

        update_membership(subscription)

        membership.refresh_from_db()
        self.assertEqual(membership.status, "past_due")
        self.assertEqual(membership.membership_type, new_type)

    def test_raises_if_subscription_not_found(self):
        """Test that an error is raised if the subscription is not found."""
        Membership.objects.create(
            user=self.user,
            membership_type=self.membership_type,
            stripe_subscription_id="sub_123",
            status=Membership.Status.ACTIVE,
        )

        subscription = Mock()
        subscription.id = "sub_unknown"
        subscription.status = "canceled"
        subscription.items = Mock()
        subscription.items.data = [Mock()]
        subscription.items.data[0].price = Mock()
        subscription.items.data[0].price.id = "price_123"

        with self.assertRaises(Membership.DoesNotExist):
            update_membership(subscription)


class TestCancelMembership(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser4",
            email="test4@example.com",
            password="testpass",
        )
        self.membership_type = MembershipType.objects.create(
            name="Standard",
            slug="standard",
            price=100,
            stripe_product_id="prod_123",
            stripe_price_id="price_123",
            is_available=True,
        )

    def test_happy_path_cancels_membership(self):
        """Test that a membership is canceled correctly."""
        membership = Membership.objects.create(
            user=self.user,
            membership_type=self.membership_type,
            stripe_subscription_id="sub_123",
            status=Membership.Status.ACTIVE,
        )

        ended_at_ts = int(datetime(2026, 10, 1, tzinfo=timezone.utc).timestamp())
        subscription = Mock()
        subscription.id = "sub_123"
        subscription.status = "canceled"
        subscription.ended_at = ended_at_ts

        cancel_membership(subscription)

        membership.refresh_from_db()
        self.assertEqual(membership.status, Membership.Status.CANCELED)

        expected_ended_at = datetime(2026, 10, 1, tzinfo=timezone.utc)
        self.assertEqual(membership.ended_at, expected_ended_at)

    def test_raises_if_subscription_not_found(self):
        """Test that an error is raised if the subscription is not found."""
        Membership.objects.create(
            user=self.user,
            membership_type=self.membership_type,
            stripe_subscription_id="sub_123",
            status=Membership.Status.ACTIVE,
        )

        subscription = Mock()
        subscription.id = "sub_456"
        subscription.status = "canceled"
        subscription.ended_at = 1_700_000_000

        with self.assertRaises(Membership.DoesNotExist):
            cancel_membership(subscription)
