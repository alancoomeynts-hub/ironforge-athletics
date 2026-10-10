from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from community.models import Post
from membership.models import Membership, MembershipType
from shop.models import Order
from user_profile.models import Profile


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alan",
            email="alan@example.com",
            password="testpass123",
            first_name="Alan",
            last_name="Smith",
        )

        self.profile, _ = Profile.objects.get_or_create(user=self.user)

        self.dashboard_url = reverse("user_profile:dashboard")
        self.login_url = reverse("account_login")

    def test_dashboard_requires_login(self):
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_dashboard_renders_for_logged_in_user(self):
        self.client.login(
            username="alan",
            password="testpass123",
        )

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_profile/dashboard.html")
        self.assertEqual(response.context["user"], self.user)
        self.assertEqual(response.context["profile"], self.profile)

    def test_dashboard_shows_user_order_history(self):
        Order.objects.create(
            user=self.user,
            status=Order.Status.PAID,
            shipping_method=Order.ShippingMethod.PICKUP,
            email="alan@example.com",
        )

        self.client.login(
            username="alan",
            password="testpass123",
        )

        response = self.client.get(self.dashboard_url)

        self.assertEqual(
            len(response.context["order_history"]),
            1,
        )

    def test_dashboard_shows_current_membership(self):
        membership_type = MembershipType.objects.create(
            name="Standard",
            slug="standard",
            price=29.99,
            stripe_price_id="price_test_123",
            is_available=True,
        )

        Membership.objects.create(
            user=self.user,
            membership_type=membership_type,
            status=Membership.Status.ACTIVE,
        )

        self.client.login(
            username="alan",
            password="testpass123",
        )

        response = self.client.get(self.dashboard_url)

        self.assertIsNotNone(response.context["current_membership"])
        self.assertEqual(
            response.context["current_membership"].status,
            Membership.Status.ACTIVE,
        )

    def test_dashboard_shows_user_post_history(self):
        Post.objects.create(
            author=self.user,
            title="My first post",
            slug="my-first-post",
            status=Post.Status.PUBLISHED,
        )

        self.client.login(
            username="alan",
            password="testpass123",
        )

        response = self.client.get(self.dashboard_url)

        self.assertEqual(
            len(response.context["post_history"]),
            1,
        )


class EditProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alan",
            email="alan@example.com",
            password="testpass123",
            first_name="Alan",
            last_name="Smith",
        )

        self.profile, _ = Profile.objects.get_or_create(user=self.user)

        self.edit_url = reverse("user_profile:edit_profile")
        self.dashboard_url = reverse("user_profile:dashboard")

    def test_edit_profile_requires_login(self):
        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_get_edit_profile_renders_form(self):
        self.client.login(
            username="alan",
            password="testpass123",
        )

        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_profile/edit_profile.html")
        self.assertIsNotNone(response.context["user_form"])
        self.assertIsNotNone(response.context["profile_form"])

    def test_valid_post_updates_user_and_profile(self):
        self.client.login(
            username="alan",
            password="testpass123",
        )

        response = self.client.post(
            self.edit_url,
            {
                "username": "alan",
                "first_name": "Alan",
                "last_name": "Jones",
                "email": "alan@example.com",
                "bio": "Strength training enthusiast",
            },
            follow=True,
        )

        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(self.user.last_name, "Jones")
        self.assertEqual(self.profile.bio, "Strength training enthusiast")
        self.assertRedirects(response, self.dashboard_url)

    def test_invalid_post_does_not_save_changes(self):
        self.client.login(
            username="alan",
            password="testpass123",
        )

        response = self.client.post(
            self.edit_url,
            {
                "username": "alan",
                "first_name": "",
                "last_name": "Smith",
                "email": "not-an-email",
                "bio": "Updated bio",
            },
        )

        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.first_name, "Alan")
        self.assertEqual(self.profile.bio, "")


class MemberProfileViewTests(TestCase):
    def setUp(self):
        self.member = User.objects.create_user(
            username="alan",
            email="alan@example.com",
            password="testpass123",
        )

        self.profile, _ = Profile.objects.get_or_create(user=self.member)

        self.member_profile_url = reverse(
            "user_profile:profile",
            args=[self.member.username],
        )

    def test_member_profile_returns_404_for_unknown_user(self):
        response = self.client.get(
            reverse(
                "user_profile:profile",
                args=["does-not-exist"],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_member_profile_renders_for_existing_user(self):
        response = self.client.get(self.member_profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "user_profile/member_profile.html")
        self.assertEqual(response.context["member"], self.member)

    def test_member_profile_shows_only_published_posts(self):
        Post.objects.create(
            author=self.member,
            title="Published post",
            slug="published-post",
            status=Post.Status.PUBLISHED,
        )

        Post.objects.create(
            author=self.member,
            title="Draft post",
            slug="draft-post",
            status=Post.Status.DRAFT,
        )

        response = self.client.get(self.member_profile_url)

        self.assertEqual(
            len(response.context["posts"]),
            1,
        )
        self.assertEqual(
            response.context["posts"][0].title,
            "Published post",
        )
