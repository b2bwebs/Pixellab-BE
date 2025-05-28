from rest_framework.throttling import UserRateThrottle


class CustomRateThrottle(UserRateThrottle):
    scope = "custom"
    """
    Dynamically determine throttle rate based on user.
    """

    def allow_request(self, request, view):
        """
        Check if the request should be throttled.
        """
        if not request.user.is_authenticated:
            return True  # Allow unauthenticated users without throttling
        # Get the throttle rate limit from the database for the authenticated user
        throttle_limit = request.user.client_info.rate_limit
        # Dynamically update the throttle rates
        self.rate = throttle_limit
        self.num_requests = throttle_limit
        # Call the parent class's allow_request method
        return super().allow_request(request, view)
