from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from clients.serializers import (
    ClientCreateUpdateSerializer,
    ClientListSerializer,
    ClientRetrieveSerializer,
    ClientSelfRetrieveSerializer,
)
from clients.models import Client

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from clients.permissions import (
    IsAdminUser,
)
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination


class ClientListApiView(ListAPIView):
    serializer_class = ClientListSerializer
    queryset = Client.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = LimitOffsetPagination


class ClientCreateAPIView(CreateAPIView):
    # email and notification pending
    serializer_class = ClientCreateUpdateSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )
    queryset = Client.objects.all()


class ClientRetrieveAPIView(RetrieveAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientRetrieveSerializer
    authentication_classes = [JWTAuthentication, IsAdminUser]
    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )


class ClientUpdateAPIView(UpdateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientCreateUpdateSerializer
    authentication_classes = [JWTAuthentication, IsAdminUser]
    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )


class ClientSelfRetrieveAPIView(RetrieveAPIView):
    serializer_class = ClientSelfRetrieveSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = (IsAuthenticated,)

    # we want to get free pack tagged,current active pack
    def get_object(self):
        # Assuming your Client model has a OneToOneField with the User model
        return self.request.user.client_info

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        response_data = {
            "client_data": serializer.data,
        }

        return Response(response_data)


client_list_view = ClientListApiView.as_view()
client_create_view = ClientCreateAPIView.as_view()
client_retrieve_view = ClientRetrieveAPIView.as_view()
client_update_view = ClientUpdateAPIView.as_view()
client_self_retrieve_view = ClientSelfRetrieveAPIView.as_view()
