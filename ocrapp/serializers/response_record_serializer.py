from rest_framework import serializers
from ocrapp.models import FileUploadRecord


class FileUploadRecordSerializer(serializers.ModelSerializer):
    doc_type_display = serializers.CharField(
        source="get_doc_type_display", read_only=True
    )
    pixellab_ai_data = serializers.CharField(source="mistral_response", read_only=True)

    class Meta:
        model = FileUploadRecord
        # fields = "__all__"
        fields = [
            "id",
            "file_name",
            "total_pages",
            "is_ai_processed",
            "is_client_fetched_response",
            "unique_id",
            "pixellab_ai_data",
            "doc_type_display",
        ]


class FileUploadRecordMarkFetchedSerializer(serializers.Serializer):
    unique_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=False)
