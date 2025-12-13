
from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read-only access to anyone,
    but write access only to staff/superusers (admins).
    """

    def has_permission(self, request, view):
        # 1. Allow GET, HEAD, or OPTIONS requests (Read permissions) to any user.
        if request.method in permissions.SAFE_METHODS:
            return True

        
        return request.user and request.user.is_staff