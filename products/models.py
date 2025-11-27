from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
import uuid


class Brand(models.Model):
    """Brand model for skincare products."""
    
    brand_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    brand_name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['brand_name']
    
    def __str__(self):
        return self.brand_name


class Category(models.Model):
    """Category model for skincare products."""
    
    category_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    category_name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['category_name']
    
    def __str__(self):
        return self.category_name


class Product(models.Model):
    """Product model for skincare items."""
    
    product_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    product_name = models.CharField(max_length=255)
    product_image = models.ImageField(
        upload_to='products/images/',
        blank=True,
        null=True,
        help_text='Upload product image. Images will be stored in media/products/images/'
    )
    product_image_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text='Or provide image URL (e.g., from CDN or external API)'
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='products'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )
    product_details = models.TextField(
        help_text='HTML-supported product details and description'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text='Price in BDT'
    )
    available_stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Number of items available in stock'
    )
    featured = models.BooleanField(
        default=False,
        help_text='Featured products will be highlighted on the homepage'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product_name} - {self.brand.brand_name}"
    
    def get_image_url(self):
        """Return image URL, prioritizing uploaded image over URL field."""
        if self.product_image:
            return self.product_image.url
        elif self.product_image_url:
            return self.product_image_url
        return None
    
    def is_in_stock(self):
        """Check if product is available in stock."""
        return self.available_stock > 0
    
    def get_stock_status(self):
        """Return stock status string."""
        if self.available_stock == 0:
            return "Out of Stock"
        elif self.available_stock < 10:
            return f"Low Stock ({self.available_stock} left)"
        else:
            return "In Stock"


class Order(models.Model):
    """Order model for managing product orders and shopping cart."""
    
    order_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    in_cart = models.BooleanField(
        default=True,
        help_text='True if items are in cart, False if order is completed'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp when the order was completed'
    )
    
    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
    
    def __str__(self):
        status = "Cart" if self.in_cart else "Completed"
        return f"Order {str(self.order_id)[:8]} - {self.user.email} ({status})"
    
    def get_total_items(self):
        """Get total number of items in the order."""
        return sum(item.quantity for item in self.items.all()) if self.pk else 0
    
    def get_total_price(self):
        """Calculate total price of the order."""
        return sum(item.get_subtotal() for item in self.items.all()) if self.pk else 0
    
    def complete_order(self):
        """
        Complete the order and update stock levels.
        Returns True if successful, False if insufficient stock.
        """
        from django.utils import timezone
        
        # Check stock availability for all items
        for item in self.items.all():
            if item.product.available_stock < item.quantity:
                return False
        
        # Update stock for each item
        for item in self.items.all():
            item.product.available_stock -= item.quantity
            item.product.save()
        
        # Mark order as completed
        self.in_cart = False
        self.completed_at = timezone.now()
        self.save()
        
        return True


class OrderItem(models.Model):
    """OrderItem model for individual products in an order."""
    
    order_item_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Number of items for this product'
    )
    price_at_purchase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Price of the product at the time of adding to cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        ordering = ['-created_at']
        unique_together = ['order', 'product']
    
    def __str__(self):
        return f"{self.quantity}x {self.product.product_name} in Order {str(self.order.order_id)[:8]}"
    
    def get_subtotal(self):
        """Calculate subtotal for this order item."""
        if self.price_at_purchase is None:
            return 0
        return self.quantity * self.price_at_purchase
    
    def save(self, *args, **kwargs):
        """Override save to set price_at_purchase if not set."""
        if not self.price_at_purchase and self.product:
            self.price_at_purchase = self.product.price
        super().save(*args, **kwargs)
