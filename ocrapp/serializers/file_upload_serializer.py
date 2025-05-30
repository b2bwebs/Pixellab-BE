from rest_framework import serializers
from ocrapp.models import FileUploadRecord


class MultipleFileUploadSerializer(serializers.Serializer):
    original_file_path = serializers.ListField(
        child=serializers.FileField(),
        allow_empty=False,
        write_only=True,
    )


class FileUploadRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUploadRecord
        fields = "__all__"
        read_only_fields = (
            "endpoint",
            "request_ip",
            "request_domain",
            "file_name",
            "doc_type",
            "total_pages",
            "finalized_pages",
            "modified_file_path",
            "user",
            "authentication_type",
        )
