

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ProductViewSet, CartItemViewSet, OrderViewSet

# Create a router instance
router = DefaultRouter()

# Register ViewSets with the router
router.register('products', ProductViewSet, basename='product') 
router.register('cart/items', CartItemViewSet, basename='cart-item')
router.register('orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]