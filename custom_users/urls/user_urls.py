from django.urls import path
from custom_users.views import (
    user_List_view,
    user_create_view,
    user_retrieve_view,
    user_update_view,
    user_delete_view,
)

urlpatterns = [
    path("list", user_List_view, name="users-list"),
    path(
        "create",
        user_create_view,
        name="users-create",
    ),
    path(
        "edit/<int:pk>/",
        user_retrieve_view,
        name="users-retrieve",
    ),
    path(
        "update/<int:pk>/",
        user_update_view,
        name="users-update",
    ),
    path(
        "<int:pk>/delete/",
        user_delete_view,
        name="users-delete",
    ),
]
