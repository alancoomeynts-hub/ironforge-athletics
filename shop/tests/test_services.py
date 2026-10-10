from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from shop.models import Category, Order, Product
from shop.services import update_order_paid


class UpdateOrderPaidTests(TestCase):
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
        )

        self.session = type(
            "Session",
            (),
            {
                "client_reference_id": str(self.order.id),
                "payment_intent": "pi_test_123",
            },
        )()

        self.payment_intent = type(
            "PaymentIntent",
            (),
            {
                "latest_charge": type(
                    "Charge",
                    (),
                    {"receipt_url": "https://example.com/receipt"},
                )()
            },
        )()

    @patch("shop.services.stripe.PaymentIntent.retrieve")
    def test_pending_order_is_marked_paid(self, mock_retrieve):
        mock_retrieve.return_value = self.payment_intent

        response = update_order_paid(self.session)

        self.assertEqual(response.status_code, 200)

        self.order.refresh_from_db()

        self.assertEqual(self.order.status, Order.Status.PAID)
        self.assertEqual(
            self.order.stripe_payment_intent_id,
            "pi_test_123",
        )
        self.assertEqual(
            self.order.stripe_receipt_url,
            "https://example.com/receipt",
        )

        mock_retrieve.assert_called_once_with(
            "pi_test_123",
            expand=["latest_charge"],
        )

    @patch("shop.services.stripe.PaymentIntent.retrieve")
    def test_already_paid_order_is_not_updated_again(self, mock_retrieve):
        self.order.status = Order.Status.PAID
        self.order.stripe_payment_intent_id = "pi_existing_123"
        self.order.save()

        response = update_order_paid(self.session)

        self.assertEqual(response.status_code, 200)

        self.order.refresh_from_db()

        # The existing payment intent should remain unchanged.
        self.assertEqual(
            self.order.stripe_payment_intent_id,
            "pi_existing_123",
        )

        # Stripe should not be called for an already-paid order.
        mock_retrieve.assert_not_called()

    def test_unknown_order_returns_404(self):
        self.session.client_reference_id = "999999"

        response = update_order_paid(self.session)

        self.assertEqual(response.status_code, 404)
