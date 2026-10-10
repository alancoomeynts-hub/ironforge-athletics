from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

import stripe

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from membership.models import Membership, MembershipType
from shop.models import Category, Order, OrderItem, Product


class PaymentProcessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alan",
            email="alan@example.com",
            password="testpass123",
        )

        self.category = Category.objects.create(
            name="Protein",
            slug="protein",
        )

        self.product = Product.objects.create(
            name="Whey Protein",
            slug="whey-protein",
            category=self.category,
            price=Decimal("29.99"),
            is_available=True,
        )

        self.order = Order.objects.create(
            user=self.user,
            status=Order.Status.PENDING,
            shipping_method=Order.ShippingMethod.DELIVERY,
            shipping_cost=Decimal("5.00"),
            email="alan@example.com",
        )

        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            price=self.product.price,
            quantity=2,
        )

        self.client.login(
            username="alan",
            password="testpass123",
        )

        self.process_url = reverse("payment:process")
        self.success_url = reverse("payment:success")
        self.canceled_url = reverse("payment:canceled")

        self.session = SimpleNamespace(
            url="https://checkout.stripe.com/receipt",
        )

    def test_payment_process_requires_login(self):
        self.client.logout()

        response = self.client.get(self.process_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_missing_order_returns_404(self):
        self.client.logout()

        self.client.login(
            username="alan",
            password="testpass123",
        )

        response = self.client.get(self.process_url)

        self.assertEqual(response.status_code, 404)

    def test_get_payment_process_renders_page(self):
        session = self.client.session
        session["order_id"] = self.order.id
        session.save()

        response = self.client.get(self.process_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "payment/process.html")

    @patch("payment.views.stripe.checkout.Session.create")
    def test_post_payment_process_creates_checkout_session(
        self,
        mock_create_session,
    ):
        mock_create_session.return_value = self.session

        session = self.client.session
        session["order_id"] = self.order.id
        session.save()

        response = self.client.post(self.process_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            "https://checkout.stripe.com/receipt",
        )


class SubscribeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alan",
            email="alan@example.com",
            password="testpass123",
        )

        self.membership_type = MembershipType.objects.create(
            name="Standard",
            slug="standard",
            price=Decimal("29.99"),
            stripe_price_id="price_test_123",
            is_available=True,
        )

        self.subscribe_url = reverse(
            "payment:subscribe",
            args=[self.membership_type.slug],
        )

        self.dashboard_url = reverse("user_profile:dashboard")
        self.join_url = reverse("membership:join")

        self.checkout_session = SimpleNamespace(
            url="https://checkout.stripe.com/subscribe",
        )

    def test_subscribe_requires_login(self):
        response = self.client.get(self.subscribe_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_existing_member_cannot_subscribe_again(self):
        Membership.objects.create(
            user=self.user,
            membership_type=self.membership_type,
            status=Membership.Status.ACTIVE,
        )

        self.client.login(
            username="alan",
            password="testpass123",
        )

        response = self.client.get(self.subscribe_url)

        self.assertRedirects(response, self.dashboard_url)

    @patch("payment.views.stripe.checkout.Session.create")
    def test_available_membership_type_creates_subscription_checkout(
        self,
        mock_create_session,
    ):
        mock_create_session.return_value = self.checkout_session

        self.client.login(
            username="alan",
            password="testpass123",
        )

        response = self.client.get(self.subscribe_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            "https://checkout.stripe.com/subscribe",
        )

        session_data = mock_create_session.call_args.kwargs

        self.assertEqual(session_data["mode"], "subscription")
        self.assertEqual(
            session_data["client_reference_id"],
            str(self.user.id),
        )
        self.assertEqual(
            session_data["metadata"]["membership_type_id"],
            str(self.membership_type.pk),
        )

    @patch("payment.views.stripe.checkout.Session.create")
    def test_stripe_error_redirects_to_join_page(
        self,
        mock_create_session,
    ):
        mock_create_session.side_effect = stripe.error.StripeError(
            "Stripe is unavailable"
        )

        self.client.login(
            username="alan",
            password="testpass123",
        )

        response = self.client.get(self.subscribe_url)

        self.assertRedirects(response, self.join_url)
