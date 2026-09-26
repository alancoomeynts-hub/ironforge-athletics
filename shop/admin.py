from django.contrib import admin

from shop.models import Category, Product, ProductReview, OrderItem, Order

# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductReview)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    list_display = (
        "id",
        "product",
        "price",
        "quantity",
    )
    readonly_fields = ("line_total_display",)

    @admin.display(description="Line total")
    def line_total_display(self, obj):
        if obj.pk:
            return obj.line_total
        return ""


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "created_on",
        "grand_total_display",
        "full_name",
        "email",
        "phone_number",
        "street_address1",
        "street_address2",
        "eircode",
        "town_or_city",
        "county",
        "stripe_receipt_url"
    )

    search_fields = (
        "id",
        "user__username",
        "user__email",
        "email",
        "stripe_payment_intent_id",
    )

    readonly_fields = (
        "created_on",
        "updated_on",
        "stripe_payment_intent_id",
        "grand_total_display",
    )

    list_filter = (
        "status",
        "created_on",
    )
    inlines = [
        OrderItemInline,
    ]

    @admin.display(description="Grand Total")
    def grand_total_display(self, obj):
        return obj.grand_total
