from django.test import TestCase

from shop.forms import CartAddProductForm, OrderForm, ProductReviewForm


class CartAddProductFormTests(TestCase):
    def test_valid_quantity_is_accepted(self):
        form = CartAddProductForm(data={"quantity": "3", "override": "on"})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["quantity"], 3)
        self.assertTrue(form.cleaned_data["override"])

    def test_invalid_quantity_is_rejected(self):
        form = CartAddProductForm(data={"quantity": "21", "override": ""})

        self.assertFalse(form.is_valid())
        self.assertIn("quantity", form.errors)

    def test_missing_quantity_is_rejected(self):
        form = CartAddProductForm(data={"override": ""})

        self.assertFalse(form.is_valid())
        self.assertIn("quantity", form.errors)


class ProductReviewFormTests(TestCase):
    def test_valid_review_is_accepted(self):
        form = ProductReviewForm(
            data={
                "rating": 5,
                "comment": "Great product, would buy again.",
            }
        )

        self.assertTrue(form.is_valid())

    def test_missing_rating_is_rejected(self):
        form = ProductReviewForm(data={"comment": "Great product."})

        self.assertFalse(form.is_valid())
        self.assertIn("rating", form.errors)

    def test_missing_comment_is_rejected(self):
        form = ProductReviewForm(data={"rating": 4})

        self.assertFalse(form.is_valid())
        self.assertIn("comment", form.errors)


class OrderFormTests(TestCase):
    def get_valid_data(self):
        return {
            "full_name": "Alan Coomey",
            "email": "alan@example.com",
            "phone_number": "0871234567",
            "shipping_method": "delivery",
            "country": "Ireland",
            "eircode": "T12 AB34",
            "town_or_city": "Cork",
            "street_address1": "123 Main Street",
            "county": "Cork",
        }

    def test_valid_delivery_order_is_accepted(self):
        form = OrderForm(data=self.get_valid_data())
        self.assertTrue(form.is_valid())

    def test_missing_required_fields_are_rejected(self):
        form = OrderForm(data={})

        self.assertFalse(form.is_valid())

        for field in (
            "email",
            "phone_number",
            "shipping_method",
            "country",
            "eircode",
            "town_or_city",
            "street_address1",
            "county",
        ):
            self.assertIn(field, form.errors)

    def test_invalid_email_is_rejected(self):
        data = self.get_valid_data()
        data["email"] = "not-an-email"

        form = OrderForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_invalid_shipping_method_is_rejected(self):
        data = self.get_valid_data()
        data["shipping_method"] = "teleportation"

        form = OrderForm(data=data)

        self.assertFalse(form.is_valid())
        self.assertIn("shipping_method", form.errors)
