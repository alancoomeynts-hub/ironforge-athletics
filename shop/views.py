from django.shortcuts import render,get_object_or_404,redirect
from django.views.decorators.http import require_POST
from .models import Category,Product, ProductReview
from .cart import Cart
from .forms import CartAddProductForm

# Create your views here.
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products=Product.objects.filter(is_available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    products=products.order_by('name')
    return render(
        request,
        'shop/product_list.html',
        {'category': category, 'categories': categories, 'products': products}
    )

def product_detail(request, id, slug):
    product=get_object_or_404(Product, id=id, slug=slug, is_available=True)
    cart_product_form=CartAddProductForm()
    return render(request,"shop/product_detail.html",{'product':product,'cart_product_form':cart_product_form})

def cart_detail(request):
    cart=Cart(request)
    return render(request,'shop/cart.html',{'cart':cart})

@require_POST
def cart_add(request,product_id):
    cart=Cart(request)
    product=get_object_or_404(Product,id=product_id)
    form=CartAddProductForm(request.POST)
    if form.is_valid():
        cd=form.cleaned_data
        cart.add_to_cart(product=product,quantity=cd['quantity'],override_quantity=cd['override'])
    return redirect('shop:cart_detail')

@require_POST
def cart_remove(request,product_id):
    cart=Cart(request)
    product=get_object_or_404(Product,id=product_id)
    cart.remove_from_cart(product)
    return redirect('shop:cart_detail')