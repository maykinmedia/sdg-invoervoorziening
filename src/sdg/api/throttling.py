from rest_framework.throttling import UserRateThrottle


class CustomRateThrottle(UserRateThrottle):
    def allow_request(self, request, view):
        """Throttle access to the API for non-authenticated users."""
        if request.auth:
            return True  # unlimited
        return super().allow_request(request, view)
