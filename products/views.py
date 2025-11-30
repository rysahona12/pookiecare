from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Brand, Category


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
