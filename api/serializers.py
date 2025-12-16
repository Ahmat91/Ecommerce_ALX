# api/serializers.py

from rest_framework import serializers
from .models import Category, Product, CartItem, Order, OrderItem
from django.db import transaction

# 1. Category Serializer (Read/Write for simple category management)
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
        read_only_fields = ['id']

# 2. Product Serializer (Read/Write for CRUD)
class ProductSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source='category', read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    is_in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock_quantity', 
            'image_url', 'created_date', 
            'category_id', 'category_detail', 'is_in_stock'
        ]
        read_only_fields = ['id', 'created_date']

    def get_is_in_stock(self, obj):
        return obj.stock_quantity > 0

# ----------------------------------------------------------------------
# CART & ORDER SERIALIZERS (Week 3 & 4 Logic)
# ----------------------------------------------------------------------

# 3. CartItem Read Serializer (To display items in the cart)
class SimpleProductSerializer(serializers.ModelSerializer):
    """Minimal product data needed within the cart view."""
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'image_url', 'stock_quantity']

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True) # Used for adding/updating items
    sub_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'sub_total']
        read_only_fields = ['user']

    def get_sub_total(self, obj):
        return obj.quantity * obj.product.price

    def validate(self, data):
        # Validation for adding/updating cart item
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        if not product_id or quantity is None:
            raise serializers.ValidationError("Product ID and quantity are required.")
        
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")
        
        if quantity <= 0:
            raise serializers.ValidationError("Quantity must be positive.")

        if quantity > product.stock_quantity:
            raise serializers.ValidationError(f"Only {product.stock_quantity} units of {product.name} are in stock.")

        return data

# 4. OrderItem Serializer (Snapshot for order history)
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'name', 'quantity', 'price_at_purchase']
        read_only_fields = fields # Order items are permanent records

# 5. Order Serializer (Read/Write for history and creation)
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status = serializers.CharField(read_only=True) # Status should not be set by API user
    
    # Custom field to accept a "cart" signal for order creation
    place_order = serializers.BooleanField(write_only=True, required=False)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'total_amount', 'status', 'created_at', 'items', 'place_order']
        read_only_fields = ['user', 'total_amount', 'created_at']

    @transaction.atomic
    def create(self, validated_data):
        """Transactional logic to move items from cart to order."""
        user = self.context['request'].user
        
        # 1. Retrieve cart items for the user
        cart_items = CartItem.objects.filter(user=user).select_related('product')

        if not cart_items.exists():
            raise serializers.ValidationError("Cannot place an order with an empty cart.")
        
        # 2. Calculate total and check stock again (critical security check)
        total_amount = sum(item.quantity * item.product.price for item in cart_items)

        # 3. Create the Order
        order = Order.objects.create(user=user, total_amount=total_amount)

        # 4. Create OrderItems and deduct stock
        order_items_to_create = []
        for cart_item in cart_items:
            product = cart_item.product
            
            # Final stock validation
            if cart_item.quantity > product.stock_quantity:
                raise serializers.ValidationError(f"Insufficient stock for {product.name}.")
                
            # Create OrderItem snapshot
            order_items_to_create.append(OrderItem(
                order=order,
                product=product,
                name=product.name,
                quantity=cart_item.quantity,
                price_at_purchase=product.price 
            ))
            
            # Deduct stock
            product.stock_quantity -= cart_item.quantity
            product.save() # Save product with new stock level

        OrderItem.objects.bulk_create(order_items_to_create)

        # 5. Clear the Cart
        cart_items.delete()

        return order