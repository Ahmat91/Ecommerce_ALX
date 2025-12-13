# api/admin.py
# Registers models with the Django Admin and customizes the interface.

from django.contrib import admin
from django.db import models
# Import Product and Category models
from .models import Category, Product 

# Register Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for the Category model."""
    list_display = ('name', 'id')
    search_fields = ('name',)
    list_per_page = 25 

# Register Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for the Product model, including custom actions and image display."""
    
    # Fields to display in the list view (NOW INCLUDES 'image_tag')
    list_display = ('name', 'category', 'price', 'stock_quantity', 'is_in_stock', 'image_tag', 'created_date')
    
    # Fields to use for filtering in the sidebar
    list_filter = ('category', 'created_date', 'stock_quantity', 'price')
    
    # Fields to search across
    search_fields = ('name', 'description')
    
    # Read-only fields. Add 'image_tag' here to display the thumbnail on the edit page.
    readonly_fields = ('created_date', 'image_tag')
    
    # Custom actions available from the list view dropdown
    actions = ['increase_stock', 'decrease_stock']

    @admin.action(description='Increase stock for selected products by 10 units')
    def increase_stock(self, request, queryset):
        """Increases stock_quantity for selected products by 10."""
        updated_count = queryset.update(stock_quantity=models.F('stock_quantity') + 10)
        self.message_user(request, f"{updated_count} product(s) stock successfully increased by 10 units.")

    @admin.action(description='Decrease stock for selected products by 10 units')
    def decrease_stock(self, request, queryset):
        """Decreases stock_quantity for selected products by 10."""
        # Loop to ensure stock doesn't drop below zero conceptually
        for product in queryset:
            if product.stock_quantity >= 10:
                product.stock_quantity -= 10
                product.save()
            else:
                # Set to 0 if subtraction would result in negative stock
                product.stock_quantity = 0
                product.save()
        
        self.message_user(request, f"Stock for selected product(s) successfully decreased.")