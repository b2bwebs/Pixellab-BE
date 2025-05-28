from rest_framework.pagination import LimitOffsetPagination


class CustomLimitOffsetPagination(LimitOffsetPagination):
    def paginate_queryset(self, queryset, request, view=None):
        if request.query_params.get("disable_pagination", "false").lower() == "true":
            return None  # Returning None disables pagination
        return super().paginate_queryset(queryset, request, view)
