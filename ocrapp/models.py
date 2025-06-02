from django.db import models
from custom_users.models import BaseModel
from django.conf import settings

TYPE_OF_DOCS = (
    (0, "PDF"),
    (1, "WORD"),
    (2, "EXCEL"),
    (3, "IMAGE"),
    (4, "TXT"),
    (5, "HTML"),
    (6, "EMAIL"),
)
User = settings.AUTH_USER_MODEL


class FileUploadRecord(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
    )
    authentication_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    endpoint = models.CharField(max_length=255)
    request_ip = models.GenericIPAddressField()
    request_domain = models.CharField(max_length=255)
    original_file_path = models.FileField(upload_to="uploads/", blank=True, null=True)
    modified_file_path = models.FileField(
        upload_to="uploads/modified/", blank=True, null=True
    )
    file_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    total_pages = models.PositiveIntegerField(blank=True, null=True)
    finalized_pages = models.PositiveIntegerField(blank=True, null=True)
    client_file_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    is_ai_processed = models.BooleanField(default=False)
    is_client_fetched_response = models.BooleanField(default=False)
    is_batched_call = models.BooleanField(default=True)
    doc_type = models.PositiveSmallIntegerField(
        choices=TYPE_OF_DOCS, blank=True, default=0
    )
    # Additional Mistral metadata
    ai_uploaded_file_id = models.CharField(max_length=255, blank=True, null=True)
    signed_url = models.CharField(max_length=255, blank=True, null=True)
    batch_file_id = models.CharField(max_length=255, blank=True, null=True)
    input_tokens = models.PositiveIntegerField(null=True, blank=True)
    output_tokens = models.PositiveIntegerField(null=True, blank=True)
    total_tokens = models.PositiveIntegerField(null=True, blank=True)
    model_used = models.CharField(max_length=100, null=True, blank=True)
    mistral_response = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.file_name)

    @property
    def doc_type_display(self):
        return self.get_doc_type_display()

    class Meta:
        verbose_name = "File Upload Record"
        verbose_name_plural = "File Upload Records"
        db_table = "file_upload_records"
