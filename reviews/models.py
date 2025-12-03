from django.db import models
from django.contrib.auth import get_user_model

# Get the custom User model (as used by the PookieCare project)
User = get_user_model()

# Constants for the star rating choices
RATING_CHOICES = (
    (1, '1 Star (Poor)'),
    (2, '2 Stars (Fair)'),
    (3, '3 Stars (Good)'),
    (4, '4 Stars (Very Good)'),
    (5, '5 Stars (Excellent)'),
)

class Review(models.Model):
    """
    Defines the database structure for a customer review.
    Since PookieCare is an e-commerce site, reviews are usually linked to a User and a Product.
    """
    # Assuming 'products' app has a Product model—we'll link to it if available.
    # For now, we use a generic field to ensure it works without knowing the 'products' model details.
    # If the Product model is available, you would use: models.ForeignKey('products.Product', on_delete=models.CASCADE)
    product_id = models.IntegerField(
        verbose_name="Product ID",
        help_text="The internal ID of the product being reviewed."
    )
    
    # Link the review to the User who posted it (using the existing User model)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    
    # The rating given by the user
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        default=5
    )
    
    # The actual text content of the review
    comment = models.TextField(
        verbose_name="Review Comment",
        help_text="The detailed text of the review."
    )
    
    # The timestamp when the review was created
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Product Review"
        verbose_name_plural = "Product Reviews"
        # Order by newest first
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.get_rating_display()} for Product ID {self.product_id}'
