

from django.contrib import admin
from django.db import models
# IMPORTANT: Must import all models, including the new ones
from .models import Category, Product, CartItem, Order, OrderItem 

# --- Inline for Order Details ---
class OrderItemInline(admin.TabularInline):
    """Allows OrderItems to be viewed/edited directly within the Order detail page."""
    model = OrderItem
    # Use raw_id_fields for large tables to avoid slow dropdowns
    raw_id_fields = ['product'] 
    # Order item details should generally be read-only once the order is placed
    readonly_fields = ['name', 'price_at_purchase', 'quantity'] 


# --- Register Core Models ---

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for the Category model."""
    list_display = ('name', 'id')
    search_fields = ('name',)
    list_per_page = 25 

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for the Product model, including custom actions and image display."""
    
    # Fields to display in the list view (Includes 'image_tag')
    list_display = ('name', 'category', 'price', 'stock_quantity', 'is_in_stock', 'image_tag', 'created_date')
    
    # Fields to use for filtering in the sidebar
    list_filter = ('category', 'created_date', 'stock_quantity', 'price')
    
    # Fields to search across
    search_fields = ('name', 'description')
    
    # Read-only fields.
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
        for product in queryset:
            if product.stock_quantity >= 10:
                product.stock_quantity -= 10
                product.save()
            else:
                product.stock_quantity = 0
                product.save()
        self.message_user(request, f"Stock for selected product(s) successfully decreased.")


# --- Register New Models (Cart & Order Logic) ---

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin for user's current shopping cart items."""
    list_display = ('user', 'product', 'quantity')
    list_filter = ('user', 'product')
    search_fields = ('user__username', 'product__name')
    raw_id_fields = ['user', 'product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for completed orders."""
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id')
    raw_id_fields = ['user']
    readonly_fields = ('created_at', 'total_amount')
    inlines = [OrderItemInline] # Show OrderItems directly within the Order detail page