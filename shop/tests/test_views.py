from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from membership.models import Membership, MembershipType
from shop.models import Category, Product, ProductReview


class ShopViewTests(TestCase):
    def setUp(self):
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

        self.user = User.objects.create_user(
            username="alan",
            email="alan@example.com",
            password="testpass123",
        )

        self.membership_type = MembershipType.objects.create(
            name="Standard",
            slug="standard",
            price=100,
            stripe_product_id="prod_123",
            stripe_price_id="price_123",
            is_available=True,
        )

        self.membership = Membership.objects.create(
            user=self.user,
            status=Membership.Status.ACTIVE,
            membership_type=self.membership_type,
        )
        self.client.login(
            username="alan",
            password="testpass123",
        )
        self.url = reverse(
            "shop:create_review",
            args=[self.product.id, self.product.slug],
        )

    def test_product_list_shows_available_products(self):

        response = self.client.get(reverse("shop:product_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertIn(self.product, response.context["products"])

    def test_product_list_filters_by_category(self):

        response = self.client.get(
            reverse(
                "shop:product_list_by_category",
                args=[self.category.slug],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["category"], self.category)
        self.assertIn(self.product, response.context["products"])

    def test_product_detail_shows_product(self):

        response = self.client.get(
            reverse(
                "shop:product_detail",
                args=[self.product.id, self.product.slug],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertEqual(response.context["product"], self.product)

    def test_logged_in_user_can_create_review(self):

        self.client.login(username="alan", password="testpass123")

        url = reverse(
            "shop:create_review",
            args=[self.product.id, self.product.slug],
        )

        response = self.client.post(
            url,
            {"rating": 5, "comment": "Great product"},
        )

        self.assertRedirects(
            response,
            reverse(
                "shop:product_detail",
                args=[self.product.id, self.product.slug],
            ),
        )

        review = ProductReview.objects.get()
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Great product")

    def test_cart_add_requires_post(self):
        url = reverse("shop:cart_add", args=[self.product.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 405)

    def test_cart_add_adds_product_to_session_cart(self):
        url = reverse("shop:cart_add", args=[self.product.id])

        response = self.client.post(
            url,
            {"quantity": 2, "override": False},
        )

        self.assertEqual(response.status_code, 302)

        cart = self.client.session.get("cart", {})
        self.assertEqual(cart[str(self.product.id)]["quantity"], 2)

    def test_cart_remove_removes_product_from_cart(self):

        session = self.client.session
        session["cart"] = {
            str(self.product.id): {
                "quantity": 2,
                "price": str(self.product.price),
            }
        }
        session.save()

        url = reverse("shop:cart_remove", args=[self.product.id])
        response = self.client.post(url)

        self.assertRedirects(response, reverse("shop:cart_detail"))

        cart = self.client.session.get("cart", {})
        self.assertNotIn(str(self.product.id), cart)

    def test_cart_update_returns_json(self):

        session = self.client.session
        session["cart"] = {
            str(self.product.id): {
                "quantity": 1,
                "price": str(self.product.price),
            }
        }
        session.save()

        url = reverse("shop:cart_update", args=[self.product.id])
        response = self.client.post(
            url,
            {"quantity": 3, "override": True},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "success": True,
                "product_id": self.product.id,
                "quantity": 3,
                "line_total": "89.97",
                "cart_total": "89.97",
                "cart_item_count": 3,
                "type": "success",
                "message": "Quantity updated to 3",
            },
        )

    def test_cart_update_invalid_quantity_returns_400(self):

        url = reverse("shop:cart_update", args=[self.product.id])

        response = self.client.post(
            url,
            {"quantity": "not-a-number", "override": True},
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])

    def test_user_cannot_submit_two_reviews_for_same_product(self):
        # Create a review for the product.
        ProductReview.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment="Great product.",
        )
        # try to submit another review for the same product.
        response = self.client.post(
            self.url,
            {
                "rating": 4,
                "comment": "Trying to submit a second review.",
            },
        )

        # Assert view redirects to product detail page.
        self.assertRedirects(
            response,
            reverse(
                "shop:product_detail",
                args=[self.product.id, self.product.slug],
            ),
        )
        # Assert only one review exists.
        self.assertEqual(ProductReview.objects.count(), 1)
