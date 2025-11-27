from django.contrib import admin
from django.utils.html import format_html
from .models import Brand, Category, Product, Order, OrderItem


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin configuration for Brand model."""
    
    list_display = ('brand_name', 'product_count', 'created_at', 'updated_at')
    search_fields = ('brand_name',)
    readonly_fields = ('brand_id', 'created_at', 'updated_at')
    ordering = ('brand_name',)
    
    fieldsets = (
        ('Brand Information', {
            'fields': ('brand_id', 'brand_name')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def product_count(self, obj):
        """Display number of products for this brand."""
        count = obj.products.count()
        return f"{count} product{'s' if count != 1 else ''}"
    product_count.short_description = 'Products'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""
    
    list_display = ('category_name', 'product_count', 'created_at', 'updated_at')
    search_fields = ('category_name',)
    readonly_fields = ('category_id', 'created_at', 'updated_at')
    ordering = ('category_name',)
    
    fieldsets = (
        ('Category Information', {
            'fields': ('category_id', 'category_name')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def product_count(self, obj):
        """Display number of products in this category."""
        count = obj.products.count()
        return f"{count} product{'s' if count != 1 else ''}"
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model."""
    
    list_display = ('product_name', 'brand', 'category', 'price_display', 
                    'stock_status', 'featured', 'created_at')
    list_filter = ('brand', 'category', 'featured', 'created_at')
    search_fields = ('product_name', 'brand__brand_name', 'category__category_name')
    readonly_fields = ('product_id', 'created_at', 'updated_at', 'image_preview')
    list_editable = ('featured',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Product Information', {
            'fields': ('product_id', 'product_name', 'brand', 'category')
        }),
        ('Product Image', {
            'fields': ('product_image', 'product_image_url', 'image_preview'),
            'description': 'Upload an image OR provide a URL. Uploaded image takes priority.'
        }),
        ('Product Details', {
            'fields': ('product_details', 'price', 'available_stock', 'featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def price_display(self, obj):
        """Display price with BDT currency."""
        return f"৳{obj.price:,.2f}"
    price_display.short_description = 'Price'
    price_display.admin_order_field = 'price'
    
    def stock_status(self, obj):
        """Display stock status with color coding."""
        status = obj.get_stock_status()
        if obj.available_stock == 0:
            color = 'red'
        elif obj.available_stock < 10:
            color = 'orange'
        else:
            color = 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status
        )
    stock_status.short_description = 'Stock Status'
    
    def image_preview(self, obj):
        """Display image preview in admin."""
        image_url = obj.get_image_url()
        if image_url:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px;" />',
                image_url
            )
        return "No image"
    image_preview.short_description = 'Image Preview'


class OrderItemInline(admin.TabularInline):
    """Inline admin for OrderItem."""
    
    model = OrderItem
    extra = 0
    readonly_fields = ('order_item_id', 'price_at_purchase', 'subtotal_display', 
                       'created_at', 'updated_at')
    fields = ('product', 'quantity', 'price_at_purchase', 'subtotal_display')
    
    def subtotal_display(self, obj):
        """Display subtotal for the order item."""
        if obj.pk and obj.price_at_purchase is not None:
            return f"৳{obj.get_subtotal():,.2f}"
        return "N/A"
    subtotal_display.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model."""
    
    list_display = ('order_id_short', 'user', 'status_display', 'total_items', 
                    'total_price_display', 'created_at', 'completed_at')
    list_filter = ('in_cart', 'created_at', 'completed_at')
    search_fields = ('order_id', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('order_id', 'created_at', 'updated_at', 'completed_at', 
                       'total_items', 'total_price_display')
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'user', 'in_cart')
        }),
        ('Order Summary', {
            'fields': ('total_items', 'total_price_display')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )
    
    def order_id_short(self, obj):
        """Display shortened order ID."""
        return str(obj.order_id)[:8]
    order_id_short.short_description = 'Order ID'
    
    def status_display(self, obj):
        """Display order status with color coding."""
        if obj.in_cart:
            return format_html(
                '<span style="color: orange; font-weight: bold;">🛒 In Cart</span>'
            )
        else:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Completed</span>'
            )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'in_cart'
    
    def total_items(self, obj):
        """Display total number of items."""
        return obj.get_total_items()
    total_items.short_description = 'Total Items'
    
    def total_price_display(self, obj):
        """Display total price."""
        return f"৳{obj.get_total_price():,.2f}"
    total_price_display.short_description = 'Total Price'
    
    actions = ['complete_orders']
    
    def complete_orders(self, request, queryset):
        """Admin action to complete selected orders."""
        completed = 0
        failed = 0
        
        for order in queryset.filter(in_cart=True):
            if order.complete_order():
                completed += 1
            else:
                failed += 1
        
        if completed:
            self.message_user(request, f'{completed} order(s) completed successfully.')
        if failed:
            self.message_user(
                request, 
                f'{failed} order(s) failed due to insufficient stock.',
                level='error'
            )
    complete_orders.short_description = 'Complete selected orders'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin configuration for OrderItem model."""
    
    list_display = ('order_item_id_short', 'order_status', 'product', 'quantity', 
                    'price_at_purchase_display', 'subtotal_display', 'created_at')
    list_filter = ('order__in_cart', 'created_at')
    search_fields = ('product__product_name', 'order__order_id', 'order__user__email')
    readonly_fields = ('order_item_id', 'price_at_purchase', 'subtotal_display', 
                       'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Order Item Information', {
            'fields': ('order_item_id', 'order', 'product', 'quantity')
        }),
        ('Pricing', {
            'fields': ('price_at_purchase', 'subtotal_display')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def order_item_id_short(self, obj):
        """Display shortened order item ID."""
        return str(obj.order_item_id)[:8]
    order_item_id_short.short_description = 'Item ID'
    
    def order_status(self, obj):
        """Display order status."""
        return "In Cart" if obj.order.in_cart else "Completed"
    order_status.short_description = 'Status'
    
    def price_at_purchase_display(self, obj):
        """Display price at purchase."""
        return f"৳{obj.price_at_purchase:,.2f}"
    price_at_purchase_display.short_description = 'Unit Price'
    
    def subtotal_display(self, obj):
        """Display subtotal."""
        if obj.price_at_purchase is not None:
            return f"৳{obj.get_subtotal():,.2f}"
        return "N/A"
    subtotal_display.short_description = 'Subtotal'
