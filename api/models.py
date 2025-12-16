

from django.db import models
from django.utils import timezone
from django.utils.html import mark_safe
from django.contrib.auth import get_user_model # To reference the custom User model
from django.utils.html import mark_safe 

User = get_user_model()
# 1. Category Model
class Category(models.Model):
    
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

# 2. Product Model
class Product(models.Model):

    # Foreign Key (FK) to Category for the one-to-many relationship
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='products',
        help_text="The category this product belongs to."
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    # Price uses DecimalField for financial accuracy
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    image_url = models.URLField(blank=True, null=True, help_text="URL for the product image.")
    created_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['name']
        

    def __str__(self):
        return f"{self.name} ({self.price} RWF)"
    
    def is_in_stock(self):
        """Convenience method to check stock status."""
        return self.stock_quantity > 0
    
    # Custom property for admin display
    is_in_stock.boolean = True
    is_in_stock.short_description = 'In Stock?'
    
    def image_tag(self):
        """Generates an HTML <img> tag for display in the Admin."""
        if self.image_url:
            return mark_safe(f'<img src="{self.image_url}" style="width: 100px; height: auto;" />')
        return "No Image"
    
    # Optional: Customize the column header in the Admin
    image_tag.short_description = 'Image Preview'


# 3. CartItem Model
class CartItem(models.Model):
    """
    Represents a single item in a user's current shopping cart.
    This model creates a unique combination constraint on user and product.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        # Ensures a user can only have one entry for a given product in their cart.
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.user.username}'s cart"

# 4. Order Model
class Order(models.Model):
    """Represents a final, completed order placed by a user."""
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} by {self.user.username} - {self.status}"

# 5. OrderItem Model (Week 4 Logic)
class OrderItem(models.Model):
    """
    Represents a snapshot of a product within a specific order.
    This ensures order history remains accurate even if product price changes later.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT) # Protect ensures product isn't deleted if an order exists
    name = models.CharField(max_length=255) # Snapshot of product name
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.name} for Order {self.order.id}"