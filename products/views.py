from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Product, Brand, Category, Order, OrderItem
from .forms import CheckoutForm


def home_view(request):
    """Display homepage with latest products and featured products."""
    all_products = Product.objects.filter(available_stock__gt=0).select_related('brand', 'category')
    featured_products = all_products.filter(featured=True)[:6]
    latest_products = all_products.order_by('-created_at')[:10]
    
    context = {
        'products': latest_products,
        'featured_products': featured_products,
    }
    
    return render(request, 'products/home.html', context)


def products_list_view(request):
    """Display all products with search and filters."""
    products = Product.objects.filter(available_stock__gt=0).select_related('brand', 'category')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(brand__brand_name__icontains=search_query) |
            Q(category__category_name__icontains=search_query)
        )
    
    # Filter by brand
    brand_filter = request.GET.get('brand')
    if brand_filter:
        products = products.filter(brand__brand_id=brand_filter)
    
    # Filter by category
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category__category_id=category_filter)
    
    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Sort by price
    sort_by = request.GET.get('sort')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')
    
    # Get all brands and categories for filter sidebar
    brands = Brand.objects.all()
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'brands': brands,
        'categories': categories,
        'search_query': search_query,
        'selected_brand': brand_filter,
        'selected_category': category_filter,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    }
    
    return render(request, 'products/products_list.html', context)


def product_detail_view(request, product_id):
    """Display detailed product information."""
    product = get_object_or_404(Product, product_id=product_id)
    related_products = Product.objects.filter(
        category=product.category,
        available_stock__gt=0
    ).exclude(product_id=product_id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    
    return render(request, 'products/product_detail.html', context)


@login_required
def add_to_cart_view(request, product_id):
    """Add a product to the authenticated user's cart."""
    product = get_object_or_404(Product, product_id=product_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    quantity = max(quantity, 1)
    next_url = request.POST.get('next') or reverse('products:home')

    if product.available_stock <= 0:
        messages.error(request, "This product is currently out of stock.")
        return redirect(next_url)

    if quantity > product.available_stock:
        messages.error(request, "Requested quantity exceeds available stock.")
        return redirect(next_url)

    order, _ = Order.objects.get_or_create(user=request.user, in_cart=True)
    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        product=product,
        defaults={
            'quantity': quantity,
            'price_at_purchase': product.price,
        }
    )

    if created:
        messages.success(request, f"Added {quantity} x {product.product_name} to your cart.")
    else:
        new_quantity = order_item.quantity + quantity
        if new_quantity > product.available_stock:
            messages.error(
                request,
                f"Only {product.available_stock} items available. Update quantity in cart."
            )
            return redirect(next_url)
        order_item.quantity = new_quantity
        order_item.save()
        messages.success(request, f"Updated {product.product_name} quantity in your cart.")

    return redirect(next_url)


@login_required
def cart_view(request):
    """Display the current user's shopping cart."""
    cart = (
        Order.objects.filter(user=request.user, in_cart=True)
        .prefetch_related('items__product__brand', 'items__product__category')
        .first()
    )
    items = cart.items.all() if cart else []
    total_price = cart.get_total_price() if cart else 0

    return render(
        request,
        'products/cart.html',
        {
            'cart': cart,
            'items': items,
            'total_price': total_price,
        }
    )


@login_required
def update_cart_item_view(request, order_item_id):
    """Update the quantity of a cart item or remove it if quantity < 1."""
    order_item = get_object_or_404(
        OrderItem,
        order_item_id=order_item_id,
        order__user=request.user,
        order__in_cart=True,
    )

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        order_item.delete()
        messages.success(request, "Item removed from your cart.")
        return redirect('products:cart')

    if quantity > order_item.product.available_stock:
        messages.error(request, "Requested quantity exceeds available stock.")
        return redirect('products:cart')

    order_item.quantity = quantity
    order_item.save()
    messages.success(request, "Cart updated.")
    return redirect('products:cart')


@login_required
def remove_from_cart_view(request, order_item_id):
    """Remove an item from the cart."""
    order_item = get_object_or_404(
        OrderItem,
        order_item_id=order_item_id,
        order__user=request.user,
        order__in_cart=True,
    )
    order_item.delete()
    messages.success(request, "Item removed from your cart.")
    return redirect('products:cart')

