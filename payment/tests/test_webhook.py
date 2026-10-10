import json
from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse

import stripe

from payment.models import StripeEventLog


@override_settings(STRIPE_WH_SECRET="whsec_test_secret")
class StripeWebhookViewTests(TestCase):
    def setUp(self):
        self.url = reverse("payment:stripe-webhook")
        self.event_id = "evt_test_123"

    def make_payload(self, event_type, event_object):
        return json.dumps(
            {
                "id": self.event_id,
                "type": event_type,
                "data": {"object": event_object},
            }
        )

    def make_session_data(self, mode):

        return {
            "id": "cs_test_456",
            "mode": mode,
        }

    def make_checkout_session(self, mode):

        return SimpleNamespace(
            id="cs_test_456",
            mode=mode,
        )

    def make_stripe_event(self, event_type, session):

        return SimpleNamespace(
            id=self.event_id,
            type=event_type,
            data=SimpleNamespace(object=session),
        )

    def post_webhook(self, payload, signature="valid-signature"):
        return self.client.post(
            self.url,
            data=payload,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE=signature,
        )

    def test_missing_signature_returns_400(self):
        session_data = self.make_session_data("payment")

        payload = self.make_payload(
            "checkout.session.completed",
            session_data,
        )

        response = self.client.post(
            self.url,
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(StripeEventLog.objects.count(), 0)

    @patch("payment.webhooks.stripe.Webhook.construct_event")
    def test_invalid_signature_returns_400(self, mock_construct_event):
        session_data = self.make_session_data("payment")

        payload = self.make_payload(
            "checkout.session.completed",
            session_data,
        )

        mock_construct_event.side_effect = stripe.error.SignatureVerificationError(
            "Invalid signature",
            "sig",
        )

        response = self.post_webhook(
            payload,
            signature="invalid-signature",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(StripeEventLog.objects.count(), 0)

    @patch("payment.webhooks.stripe.Webhook.construct_event")
    def test_payment_checkout_routes_to_shop_service(
        self,
        mock_construct_event,
    ):
        session_data = self.make_session_data("payment")
        session = self.make_checkout_session("payment")

        payload = self.make_payload(
            "checkout.session.completed",
            session_data,
        )

        mock_construct_event.return_value = self.make_stripe_event(
            "checkout.session.completed",
            session,
        )

        with patch("shop.services.update_order_paid") as mock_update_order:
            response = self.post_webhook(payload)

        self.assertEqual(response.status_code, 200)
        mock_update_order.assert_called_once_with(session)
        self.assertEqual(StripeEventLog.objects.count(), 1)

    @patch("payment.webhooks.stripe.Webhook.construct_event")
    def test_subscription_checkout_routes_to_membership_service(
        self,
        mock_construct_event,
    ):
        session_data = self.make_session_data("subscription")
        session = self.make_checkout_session("subscription")

        payload = self.make_payload(
            "checkout.session.completed",
            session_data,
        )

        mock_construct_event.return_value = self.make_stripe_event(
            "checkout.session.completed",
            session,
        )

        with patch("membership.services.create_membership") as mock_create_membership:
            response = self.post_webhook(payload)

        self.assertEqual(response.status_code, 200)
        mock_create_membership.assert_called_once_with(session)
        self.assertEqual(StripeEventLog.objects.count(), 1)

    @patch("payment.webhooks.stripe.Webhook.construct_event")
    def test_duplicate_event_is_processed_once(
        self,
        mock_construct_event,
    ):
        session_data = self.make_session_data("subscription")
        session = self.make_checkout_session("subscription")

        payload = self.make_payload(
            "checkout.session.completed",
            session_data,
        )

        mock_construct_event.return_value = self.make_stripe_event(
            "checkout.session.completed",
            session,
        )

        with patch("membership.services.create_membership") as mock_create_membership:
            first_response = self.post_webhook(payload)
            second_response = self.post_webhook(payload)

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)

        mock_create_membership.assert_called_once()
        self.assertEqual(StripeEventLog.objects.count(), 1)

    @patch("payment.webhooks.stripe.Webhook.construct_event")
    def test_unhandled_event_returns_200(
        self,
        mock_construct_event,
    ):
        event_object = {"id": "re_test_123"}

        payload = self.make_payload(
            "charge.refunded",
            event_object,
        )

        mock_construct_event.return_value = SimpleNamespace(
            id=self.event_id,
            type="charge.refunded",
            data=SimpleNamespace(object=event_object),
        )

        response = self.post_webhook(payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(StripeEventLog.objects.count(), 0)
