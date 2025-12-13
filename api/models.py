

from django.db import models
from django.utils import timezone
from django.utils.html import mark_safe

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
