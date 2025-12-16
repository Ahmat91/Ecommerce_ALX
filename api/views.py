# api/views.py

from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
# IMPORTANT: Need to import all models and serializers
from .models import Product, CartItem, Order
from .serializers import ProductSerializer, CartItemSerializer, OrderSerializer
from .permissions import IsAdminOrReadOnly 

# Third-party packages for filtering and search 
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


# 1. Product ViewSet (CRUD, Filtering, Searching - Weeks 1 & 2)
class ProductViewSet(viewsets.ModelViewSet):
    
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly] 
    
    # Filtering and Searching Configuration
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'stock_quantity'] 
    search_fields = ['name', 'description', 'category__name'] 
    ordering_fields = ['price', 'stock_quantity', 'created_date'] 


# 2. CartItem ViewSet (Add/Update/Delete item in cart - Week 3)
class CartItemViewSet(viewsets.GenericViewSet, 
                      mixins.ListModelMixin, 
                      mixins.CreateModelMixin, 
                      mixins.DestroyModelMixin):
    
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Ensure users only see their own cart items
        return CartItem.objects.filter(user=self.request.user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Custom logic to handle adding/updating cart items."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data.get('product_id')
        quantity = serializer.validated_data.get('quantity')
        user = self.request.user
        
        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            user=user, 
            product_id=product_id,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # If item exists, update the quantity
            cart_item.quantity = quantity
            cart_item.save()
        
        # Use a fresh serializer instance to ensure correct read representation
        read_serializer = self.get_serializer(cart_item)
        
        return Response(read_serializer.data, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)


# 3. Order ViewSet (List User Orders, Create New Order - Week 4)
class OrderViewSet(viewsets.GenericViewSet, 
                   mixins.ListModelMixin, 
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin):
    
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own orders, nested items are prefetched for efficiency
        return Order.objects.filter(user=self.request.user).prefetch_related('items')

    def perform_create(self, serializer):
       
        serializer.save()