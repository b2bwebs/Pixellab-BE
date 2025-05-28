from rest_framework.permissions import BasePermission
from constants import (
    SUPER_ADMIN,
    SUB_ADMIN,
    DATA_ANALYST,
)


class IsAllowedOrigin(BasePermission):
    def has_permission(self, request, view):
        # Ensure request has a user (authenticated)
        if not request.user.is_authenticated:
            return False
            # allowing sub admin and admin
        if request.user.role < 2:
            return True
        # Get the client associated with the authenticated user
        client = request.user.client_info

        if not client:
            return False
        # Get the origin from the request headers
        domain = request.META.get("HTTP_HOST")
        # Check if the domain with http:// or https:// is allowed for the client
        allowed_domains = [f"http://{domain}", f"https://{domain}"]
        return client.allowed_origins.filter(origin__in=allowed_domains).exists()


class IsAdminUser(BasePermission):
    """
    permission for master admin access
    """

    def has_permission(self, request, view):
        return True if request.user.role in [SUPER_ADMIN, SUB_ADMIN] else False


class IsCompanyUser(BasePermission):
    """
    permission for master admin access
    """

    def has_permission(self, request, view):
        return (
            True
            if request.user.role in [SUPER_ADMIN, SUB_ADMIN, DATA_ANALYST]
            else False
        )
