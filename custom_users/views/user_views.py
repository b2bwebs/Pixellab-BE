from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
)
from django.contrib.auth import get_user_model
from custom_users.serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)
from custom_users.pagination import CustomLimitOffsetPagination

User = get_user_model()


class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomLimitOffsetPagination


class UserCreateView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer


class UserRetrieveView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # lookup_field = "id"


class UserUpdateView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer


class UserDestroyView(DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # lookup_field = "id"


user_List_view = UserListView.as_view()
user_create_view = UserCreateView.as_view()
user_retrieve_view = UserRetrieveView.as_view()
user_update_view = UserUpdateView.as_view()
user_delete_view = UserDestroyView.as_view()
