from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Category, Product, ProductReview
from .cart import Cart
from .forms import CartAddProductForm
from django.contrib import messages


# Create your views here.
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)
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
    product = get_object_or_404(Product, id=id, slug=slug, is_available=True)
    cart_product_form = CartAddProductForm()
    return render(
        request,
        "shop/product_detail.html",
        {"product": product, "cart_product_form": cart_product_form},
    )


def cart_detail(request):
    cart = Cart(request)
    return render(
        request,
        "shop/cart.html",
        {"cart": cart},
    )


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data

        cart.add_to_cart(
            product=product,
            quantity=cd["quantity"],
            override_quantity=cd["override"],
        )

    messages.info(request, f"Product {product.name} added to cart")

    return redirect(
        "shop:product_list_by_category", category_slug=product.category.slug
    )


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove_from_cart(product)
    messages.info(request, f"Product {product.name} removed from cart")
    return redirect("shop:cart_detail")


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    form = CartAddProductForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"success": False, "error": "Invalid quantity"}, status=400)

    quantity = form.cleaned_data["quantity"]
    cart.add_to_cart(
        product=product,
        quantity=quantity,
        override_quantity=True,
    )

    message= f"Quantity updated to {quantity}"

    return JsonResponse(
        {
            "success": True,
            "product_id": product_id,
            "quantity": quantity,
            "line_total": f"{cart.get_line_total(product.id):.2f}",
            "cart_total": f"{cart.get_total_price():.2f}",
            "cart_item_count": len(cart),
            "message": message,
        }
    )
