from django.urls import path
from clients.views import (
    client_create_view,
    client_list_view,
    client_retrieve_view,
    client_update_view,
    client_self_retrieve_view,
)

urlpatterns = [
    path("create", client_create_view, name="client-create"),
    path("edit/<int:pk>/", client_retrieve_view, name="client-retrieve"),
    path(
        "self-details/", client_self_retrieve_view, name="client-retrieve-self-details"
    ),
    path("update/<int:pk>/", client_update_view, name="client_update"),
    path("list", client_list_view, name="clients-list"),
]
