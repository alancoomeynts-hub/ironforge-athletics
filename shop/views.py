from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from user_profile.decorators import staff_or_membership_required

from .cart import Cart
from .forms import CartAddProductForm, OrderForm, ProductReviewForm
from .models import Category, OrderItem, Product, ProductReview


def product_list(request, category_slug=None):
    """
    Display all available products, optionally filtered by category.
    """
    category = None
    categories = Category.objects.all()

    # Only show products that are currently available for purchase.
    products = Product.objects.filter(is_available=True)

    # If a category slug is provided, filter the product list to that category.
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    products = products.order_by("name")

    return render(
        request,
        "shop/product_list.html",
        {"category": category, "categories": categories, "products": products},
    )


def product_detail(request, id, slug):
    """
    Display an individual available product, its reviews,
    and a form for adding it to the cart.
    """
    # The product must match both its ID and slug and must be available.
    product = get_object_or_404(Product, id=id, slug=slug, is_available=True)

    cart_product_form = CartAddProductForm()

    # Gets reviews and their users together.
    product_reviews = product.reviews.select_related("user").all()
    review_form = ProductReviewForm()

    has_reviewed = False

    if request.user.is_authenticated:
        has_reviewed = product.reviews.filter(user=request.user).exists()

    return render(
        request,
        "shop/product_detail.html",
        {
            "product": product,
            "product_reviews": product_reviews,
            "review_form": review_form,
            "cart_product_form": cart_product_form,
            "has_reviewed": has_reviewed,
        },
    )


@staff_or_membership_required
@require_POST
def create_review(request, id, slug):
    """
    Allow an authorized user to submit a review for a product.
    """

    product = get_object_or_404(Product, id=id, slug=slug, is_available=True)

    # Prevent users from submitting multiple reviews for the same product.
    if ProductReview.objects.filter(
        product=product,
        user=request.user,
    ).exists():
        messages.error(
            request,
            "You have already reviewed this product.",
        )
        return redirect(
            "shop:product_detail",
            id=id,
            slug=slug,
        )

    form = ProductReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()

        messages.success(request, "Review submitted successfully!")

        return redirect(
            "shop:product_detail",
            id=id,
            slug=slug,
        )

    # If the form is invalid, redisplay the product page with errors.
    product_reviews = product.reviews.select_related("user").all()
    cart_product_form = CartAddProductForm()

    return render(
        request,
        "shop/product_detail.html",
        {
            "product": product,
            "product_reviews": product_reviews,
            "review_form": form,
            "cart_product_form": cart_product_form,
        },
    )


def cart_detail(request):
    """
    Display the contents of the current user's session-based cart.
    """
    cart = Cart(request)

    return render(
        request,
        "shop/cart.html",
        {"cart": cart},
    )


@require_POST
def cart_add(request, product_id):
    """
    Add a product to the session cart using the submitted quantity.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data

        # Add the product, either increasing its quantity or
        # replacing the existing quantity if override is selected.
        cart.add_to_cart(
            product=product,
            quantity=cd["quantity"],
            override_quantity=cd["override"],
        )

    messages.success(request, f"Product {product.name} added to cart")

    return redirect(
        "shop:product_list_by_category",
        category_slug=product.category.slug,
    )


@require_POST
def cart_remove(request, product_id):
    """
    Remove a product from the session cart.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    cart.remove_from_cart(product)

    messages.success(request, f"Product {product.name} removed from cart")

    return redirect("shop:cart_detail")


@require_POST
def cart_update(request, product_id):
    """
    Update a product's quantity in the cart and return updated
    cart totals as JSON for use by JavaScript.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    form = CartAddProductForm(request.POST)
    if not form.is_valid():
        return JsonResponse(
            {"success": False, "error": "Invalid quantity"},
            status=400,
        )

    quantity = form.cleaned_data["quantity"]
    # Replace the existing quantity rather than adding to it.
    cart.add_to_cart(
        product=product,
        quantity=quantity,
        override_quantity=True,
    )

    message = f"Quantity updated to {quantity}"

    return JsonResponse(
        {
            "success": True,
            "product_id": product_id,
            "quantity": quantity,
            "line_total": f"{cart.get_line_total(product.id):.2f}",
            "cart_total": f"{cart.get_total_price():.2f}",
            "cart_item_count": len(cart),
            "type": "success",
            "message": message,
        }
    )


@login_required
def confirm_order(request):
    """
    Create an order from the current session cart and redirect
    the user to the payment process.
    """
    cart = Cart(request)

    if request.method == "POST":
        form = OrderForm(request.POST)

        if form.is_valid():
            # Do not save immediately because the user and
            # delivery details still need to be attached.
            order = form.save(commit=False)
            order.user = request.user

            shipping_method = form.cleaned_data["shipping_method"]
            shipping_cost = Decimal(0.00)

            # Collection is free; delivery uses the configured cost.
            if shipping_method == "delivery":
                shipping_cost = Decimal(settings.DELIVERY_COSTS)

            order.shipping_method = shipping_method
            order.shipping_cost = shipping_cost
            order.save()

            # Convert each cart item into a orderItem instance.
            for item in cart:
                product = item["product"]

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=item["quantity"],
                )

            # Empty the cart once its items have been added to the order.
            cart.clear()

            # Store the order ID in the session for the payment step.
            request.session["order_id"] = order.id

            return redirect("payment:process")
    else:
        form = OrderForm()

    return render(
        request,
        "shop/confirm_order.html",
        {"cart": cart, "form": form},
    )
