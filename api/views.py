
from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer
from .permissions import IsAdminOrReadOnly 

# Third-party packages for filtering and search (required for future steps)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter


class ProductViewSet(viewsets.ModelViewSet):
    
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    # Apply the custom permission: Read-only for all, Write access for Admin/Staff
    permission_classes = [IsAdminOrReadOnly] 
    
    
    # 1. Enable DjangoFilterBackend for complex filters (e.g., price range)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Fields available for exact filtering (Category ID)
    filterset_fields = ['category', 'stock_quantity'] 
    
    # Fields available for searching (partial match)
    search_fields = ['name', 'description', 'category__name'] 
    
    # Fields available for ordering (sorting)
    ordering_fields = ['price', 'stock_quantity', 'created_date']