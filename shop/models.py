from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from decimal import Decimal


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    sku = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="products",
    )
    image = CloudinaryField("image", blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class ProductReview(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="product_reviews"
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_on",)
        constraints = [
            models.UniqueConstraint(
                fields=["product", "user"], name="unique_product_review"
            )
        ]

    def __str__(self):
        return f"{self.product.name} review ({self.user.username})"

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending',"Pending"
        PAID = 'paid',"Paid"
        FAILED = 'failed',"Failed"
        CANCELLED = 'cancelled',"Cancelled"

    class ShippingMethod(models.TextChoices):
        PICKUP = 'pickup',"Pickup"
        DELIVERY = 'delivery',"Delivery"

    user = models.ForeignKey(User, on_delete=models.PROTECT,related_name="orders",)
    status = models.CharField(max_length=20,choices=Status.choices,default=Status.PENDING,)
    shipping_method = models.CharField(max_length=20,choices=ShippingMethod.choices,default=ShippingMethod.PICKUP,)
    shipping_cost=models.DecimalField(max_digits=10,decimal_places=2,default=Decimal("0.00"),)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    stripe_payment_intent_id=models.CharField(max_length=30,blank=True,null=True,unique=True,)

    full_name = models.CharField(max_length=30,blank=True,default='',)
    email = models.EmailField(max_length=30,blank=False,null=False,)
    phone_number = models.CharField(max_length=20,blank=False,null=False,)
    country = models.CharField(max_length=15,default='IE')
    eircode = models.CharField(max_length=10)
    town_or_city = models.CharField(max_length=25)
    street_address1 = models.CharField(max_length=50)
    street_address2 = models.CharField(max_length=50)
    county = models.CharField(max_length=25)

    class Meta:
        ordering = ('-created_on',)
        indexes = [
            models.Index(fields=['-created_on']),
        ]

    def __str__(self):
        return f"Order {self.id} for {self.user.username}"

    @property
    def order_total(self):
        return sum((item.line_total for item in self.items.all()),Decimal("0"),)

    @property
    def grand_total(self):
        return self.order_total + self.shipping_cost

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"OrderItem {self.quantity} x {self.product.name}"

    @property
    def line_total(self):
        return self.quantity * self.price
