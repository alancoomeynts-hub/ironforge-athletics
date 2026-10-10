from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Membership(models.Model):
    class Status(models.TextChoices):
        INCOMPLETE = "incomplete", "Incomplete"
        INCOMPLETE_EXPIRED = "incomplete_expired", "Incomplete expired"
        TRIALING = "trialing", "Trialing"
        ACTIVE = "active", "Active"
        PAST_DUE = "past_due", "Past due"
        UNPAID = "unpaid", "Unpaid"
        PAUSED = "paused", "Paused"
        CANCELED = "canceled", "Canceled"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    membership_type = models.ForeignKey(
        "MembershipType", on_delete=models.PROTECT, related_name="memberships"
    )
    joined_date = models.DateField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    stripe_customer_id = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    stripe_checkout_session_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
    )
    last_renewal_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}--{self.membership_type}"


class MembershipType(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    stripe_product_id = models.CharField(max_length=255)
    stripe_price_id = models.CharField(max_length=255)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name
