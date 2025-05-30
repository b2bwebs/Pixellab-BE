from rest_framework.permissions import BasePermission


class IsOAuthUser(BasePermission):
    """
    Custom permission to allow only OAuth2 authenticated users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.auth and request.auth.application)


class CustomScopePermission(BasePermission):
    def has_permission(self, request, view):
        required_scope = "read"  # Replace with your custom scope
        # required_scope = "custom_scope"  # Replace with your custom scope
        if not request.auth or required_scope not in request.auth.scope:
            return False
        return True
