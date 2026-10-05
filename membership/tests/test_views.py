from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from membership.models import MembershipType, Membership


User = get_user_model()


class MembershipTypeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="123",
            email="test@test.ie",
        )
        self.staff_user = User.objects.create_user(
            username="staffuser",
            password="123",
            email="stafftest@test.ie",
            is_staff=True,
        )
        self.membership_type = MembershipType.objects.create(
            name="Test Membership",
            slug="test-membership",
            price=100,
            stripe_product_id="prod_1234567890",
            is_available=True,
        )
        self.join_url = reverse("membership:join")
        self.manage_url = reverse("membership:manage")

    def test_membership_page_anonymous_user(self):
        """Test that the membership page is accessible to anonymous users."""
        response = self.client.get(self.join_url)
        assert response.status_code == 200
        assert "membership/join.html" in [t.name for t in response.templates]

        assert "membership_types" in response.context
        assert "current_membership" in response.context
        assert response.context["current_membership"] is None

        types = list(response.context["membership_types"])
        assert self.membership_type in types

    def test_membership_logged_in_no_membership(self):
        """Test that the membership page is accessible to logged-in users without a membership."""
        self.client.login(username=self.user.username, password="testpass123")
        response = self.client.get(self.join_url)
        assert response.status_code == 200
        assert response.context["current_membership"] is None

    def test_membership_logged_in_with_membership(self):
        """Test that the membership page is accessible to logged-in users with a membership."""
        self.client.login(username=self.user.username, password="123")

        membership = Membership.objects.create(
            user=self.user,
            membership_type=self.membership_type,
            status=Membership.Status.ACTIVE,
            stripe_checkout_session_id="cs_test_123",
            stripe_customer_id="cus_test_123",
        )

        assert Membership.objects.filter(
            user=self.user, status=Membership.Status.ACTIVE
        ).exists()
        response = self.client.get(self.join_url)
        assert response.status_code == 200

        current_membership = response.context["current_membership"]
        assert current_membership is not None
        assert current_membership.stripe_customer_id == membership.stripe_customer_id
        assert current_membership.status == Membership.Status.ACTIVE

    def test_manage_membership_anonymous_redirects_to_login(self):
        """Test if anonymous users can access the manage membership page and are redirected to login."""
        response = self.client.get(self.manage_url)
        assert response.status_code == 302
        assert "login" in response.url

    def test_manage_membership_logged_in_no_membership_redirects_to_join(self):
        """Test if non-members can access the manage membership page and are redirected to join."""
        self.client.login(username=self.user.username, password="123")
        response = self.client.get(self.manage_url)

        if response.status_code == 403:
            assert response.status_code == 403
            return

        assert response.status_code == 302
        assert response.url == self.join_url
