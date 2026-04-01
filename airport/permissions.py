from rest_framework.permissions import BasePermission, SAFE_METHODS


class isAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
