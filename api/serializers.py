
from rest_framework import serializers
from .models import Category, Product

# 1. Serializer for the Category model
class CategorySerializer(serializers.ModelSerializer):
    """Serializer for reading and writing Category data."""
    class Meta:
        model = Category
        fields = ['id', 'name']
        read_only_fields = ['id']

# 2. Serializer for the Product model
class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.
    It uses the CategorySerializer for nested read representation.
    """
    
    category_detail = CategorySerializer(source='category', read_only=True)

    # Use a Writeable field (ID) for create/update operations
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    
    # Custom field to display stock status
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
        """Calculates and returns true if stock is > 0."""
        return obj.stock_quantity > 0