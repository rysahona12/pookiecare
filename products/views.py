from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Product, Brand, Category, Order, OrderItem
from .forms import CheckoutForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from io import BytesIO

try:
    import weasyprint
except Exception:  
    weasyprint = None

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except Exception:  
    canvas = None

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


@login_required
def checkout_view(request):
    """Display order form and complete the order."""
    cart = (
        Order.objects.filter(user=request.user, in_cart=True)
        .prefetch_related('items__product')
        .first()
    )

    if not cart or cart.get_total_items() == 0:
        messages.info(request, "Your cart is empty.")
        return redirect('products:home')

    user = request.user
    initial_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone_number': user.phone_number,
        'house_number': user.house_number,
        'road_number': user.road_number,
        'postal_code': user.postal_code,
        'district': user.district,
    }

    if request.method == 'POST':
        form = CheckoutForm(request.POST, initial=initial_data)
        if form.is_valid():
            # Update user's shipping/contact info for reuse
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.phone_number = form.cleaned_data['phone_number']
            user.house_number = form.cleaned_data['house_number']
            user.road_number = form.cleaned_data['road_number']
            user.postal_code = form.cleaned_data['postal_code']
            user.district = form.cleaned_data['district']
            user.save()

            success = cart.complete_order()
            if success:
                messages.success(request, "Order placed successfully! Your slip download will begin.")
                return download_print_slip_view(request, order_id=cart.order_id)
            messages.error(request, "Not enough stock to complete your order.")
            return redirect('products:cart')
    else:
        form = CheckoutForm(initial=initial_data)

    return render(
        request,
        'products/checkout.html',
        {
            'cart': cart,
            'items': cart.items.all(),
            'total_price': cart.get_total_price(),
            'form': form,
        }
    )


@login_required
def download_print_slip_view(request, order_id=None):
    """Generate a PDF slip for an order.

    If ``order_id`` is provided, the view returns the slip for that specific completed order.
    If ``order_id`` is omitted, it returns a slip for the current cart (in_cart=True).
    """
    if order_id:
        order = get_object_or_404(
            Order.objects.filter(user=request.user, in_cart=False).prefetch_related('items__product'),
            order_id=order_id,
        )
    else:
        order = (
            Order.objects.filter(user=request.user, in_cart=True)
            .prefetch_related('items__product')
            .first()
        )
        if not order:
            return HttpResponse("No active cart to print.", status=404)

    if not order.items.exists():
        return HttpResponse("No items to print for this order.", status=404)

    context = {
        'order': order,
        'items': order.items.all(),
        'total_price': order.get_total_price(),
        'user': request.user,
        'printed_at': timezone.now(),
    }

    html_string = render_to_string('products/print_slip.html', context)

    pdf_file = None

    if weasyprint is not None:
        try:
            pdf_file = weasyprint.HTML(
                string=html_string,
                base_url=request.build_absolute_uri('/'),
            ).write_pdf()
        except Exception:
            pdf_file = None 

    if pdf_file is None and canvas is not None:
        pdf_file = generate_reportlab_slip(context)

    if pdf_file is None:
        return HttpResponse(
            "PDF generation not available (WeasyPrint/ReportLab failed).",
            status=503,
        )

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.order_id}.pdf"'
    return response


def generate_reportlab_slip(context):
    """Create a styled PDF slip using ReportLab as a dependency-light fallback."""
    if canvas is None:
        return None

    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )

    order = context['order']
    items = context['items']
    total_price = context['total_price']
    user = context['user']
    printed_at = context['printed_at']

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=22 * mm,
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="Muted",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#6b6358"),
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Label",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#6b6358"),
            leading=11,
            spaceAfter=1,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Heading",
            parent=styles["Normal"],
            fontSize=18,
            textColor=colors.HexColor("#b88746"),
            leading=22,
            spaceAfter=2,
        )
    )

    full_name = getattr(user, "get_full_name", lambda: "")() or user.email
    address = getattr(user, "get_full_address", lambda: "")()
    status = "In Cart" if order.in_cart else "Completed"
    placed_at = order.completed_at or order.created_at

    story = []

    header_table = Table(
        [
            [
                Paragraph(
                    "<b>PookieCare</b><br/><font size=10 color='#6b6358'>Skin health, delivered with care.</font>",
                    styles["Heading"],
                ),
                Paragraph(
                    f"<font size=9 color='#6b6358'>Order ID</font><br/>{order.order_id}"
                    f"<br/><br/><font size=9 color='#6b6358'>Placed</font><br/>{placed_at.strftime('%b %d, %Y %H:%M')}"
                    f"<br/><br/><font size=9 color='#6b6358'>Printed</font><br/>{printed_at.strftime('%b %d, %Y %H:%M')}"
                    f"<br/><br/><font size=9 color='#b88746'>&#9632; {status}</font>",
                    styles["Normal"],
                ),
            ]
        ],
        colWidths=[doc.width * 0.55, doc.width * 0.45],
        hAlign="LEFT",
    )
    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LINEBELOW", (0, 0), (-1, 0), 0.25, colors.HexColor("#d9cbb3")),
            ]
        )
    )
    story.append(header_table)
    story.append(Spacer(1, 8))

    customer_details = [
        [
            Paragraph(
                f"<font size=9 color='#6b6358'>Name</font><br/><b>{full_name}</b>",
                styles["Normal"],
            ),
            Paragraph(
                f"<font size=9 color='#6b6358'>Phone</font><br/>{getattr(user, 'phone_number', '')}",
                styles["Normal"],
            ),
        ],
        [
            Paragraph(
                f"<font size=9 color='#6b6358'>Address</font><br/>{address}",
                styles["Normal"],
            )
        ],
    ]
    customer_inner = Table(
        customer_details,
        colWidths=[doc.width * 0.4, doc.width * 0.6],
        hAlign="LEFT",
    )
    customer_inner.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("SPAN", (0, 1), (-1, 1)),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    customer_panel = Table(
        [
            [Paragraph("<font size=9 color='#6b6358'>Customer</font>", styles["Muted"])],
            [customer_inner],
        ],
        colWidths=[doc.width],
    )
    customer_panel.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fbfaf8")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d9cbb3")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(customer_panel)
    story.append(Spacer(1, 12))

    table_data = [["Product", "Qty", "Amount (BDT)"]]
    for item in items:
        table_data.append(
            [
                item.product.product_name,
                str(item.quantity),
                f"{item.get_subtotal():.2f}",
            ]
        )
    table_data.append(["", "Total", f"{total_price:.2f}"])

    items_table = Table(
        table_data,
        colWidths=[doc.width * 0.55, doc.width * 0.15, doc.width * 0.3],
        repeatRows=1,
    )
    items_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#fbfaf8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#6b6358")),
                ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#d9cbb3")),
                ("ALIGN", (1, 1), (-1, -2), "RIGHT"),
                ("ALIGN", (1, -1), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("FONTSIZE", (0, 1), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#fbfaf8")]),
                ("LINEBELOW", (0, -2), (-1, -2), 0.25, colors.HexColor("#d9cbb3")),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("TOPPADDING", (0, -1), (-1, -1), 10),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
            ]
        )
    )
    story.append(items_table)
    story.append(Spacer(1, 14))

    footer = Paragraph(
        "Thank you for trusting PookieCare. Please retain this slip for your records.",
        styles["Muted"],
    )
    story.append(footer)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
