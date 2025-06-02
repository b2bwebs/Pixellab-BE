from rest_framework import serializers
from ocrapp.models import FileUploadRecord


class FileUploadRecordSerializer(serializers.ModelSerializer):
    doc_type_display = serializers.CharField(
        source="get_doc_type_display", read_only=True
    )

    class Meta:
        model = FileUploadRecord
        fields = "__all__"


class FileUploadRecordMarkFetchedSerializer(serializers.Serializer):
    unique_ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=False)
