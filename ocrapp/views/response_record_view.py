from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from ocrapp.permissions import CustomScopePermission
from clients.permissions import IsAllowedOrigin
from ocrapp.models import FileUploadRecord
from ocrapp.serializers import (
    FileUploadRecordSerializer,
    FileUploadRecordMarkFetchedSerializer,
)
from rest_framework.response import Response
from rest_framework import status


class FileUploadRecordListApiView(ListAPIView):
    authentication_classes = [OAuth2Authentication]
    # domain restriction permission commented for future use
    # permission_classes = [IsAuthenticated, IsAllowedOrigin]
    permission_classes = [CustomScopePermission]
    serializer_class = FileUploadRecordSerializer

    def get_queryset(self):
        return FileUploadRecord.objects.filter(is_client_fetched_response=False)


class FileUploadRecordMarkFetchedAPIView(APIView):
    authentication_classes = [OAuth2Authentication]
    # domain restriction permission commented for future use
    # permission_classes = [IsAuthenticated, IsAllowedOrigin]
    permission_classes = [CustomScopePermission]

    def post(self, request):
        serializer = FileUploadRecordMarkFetchedSerializer(data=request.data)
        if serializer.is_valid():
            unique_ids = serializer.validated_data["unique_ids"]
            updated_count = FileUploadRecord.objects.filter(
                unique_id__in=unique_ids
            ).update(is_client_fetched_response=True)
            return Response(
                {
                    "marked_count": updated_count,
                    "message": f"{updated_count} records marked as fetched.",
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


response_list_view = FileUploadRecordListApiView.as_view()
mark_fetched_view = FileUploadRecordMarkFetchedAPIView.as_view()
