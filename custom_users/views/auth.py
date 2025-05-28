from rest_framework.generics import (
    CreateAPIView,
)
from custom_users.serializers import (
    AuthSerializer,
)
from backend.response import (
    SuccessResponse,
    ErrorResponse,
)
from rest_framework.permissions import AllowAny

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status


# request allow only from our frontend domain restriction pending
class LoginView(CreateAPIView):
    serializer_class = AuthSerializer
    permission_classes = (AllowAny,)
    """
    Login using email and password
    """

    def post(self, request):
        token_serializer = AuthSerializer(data=request.data)
        if token_serializer.is_valid():
            return SuccessResponse(
                data=token_serializer.validated_data, message="Login Successful"
            )
        message = "Error"
        # print(token_serializer.errors)
        if token_serializer.errors.get("non_field_errors"):
            message = token_serializer.errors["non_field_errors"][0]
            return ErrorResponse(message=message)
        # Handling field-specific errors
        field_errors = token_serializer.errors
        field_errors_message = " ".join(
            [f"{field}: {error[0]}" for field, error in field_errors.items()]
        )
        return ErrorResponse(message=field_errors_message)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Revoke the access and refresh tokens
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                # If refresh token is not provided in the request data
                return Response(
                    {"detail": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Return success response
            return Response({"detail": "Successfully logged out."})
        except Exception as e:
            print(e)
            # Handle any errors that occur during logout
            return Response(
                {"detail": "An error occurred while logging out."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
