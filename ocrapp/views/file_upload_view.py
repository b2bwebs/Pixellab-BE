from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from ocrapp.models import FileUploadRecord
from clients.models import ClientAIParsingConfig
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.permissions import IsAuthenticated
from ocrapp.serializers import MultipleFileUploadSerializer
from ocrapp.permissions import CustomScopePermission
from clients.permissions import IsAllowedOrigin
from django.core.files import File
import os
from PyPDF2 import PdfReader, PdfWriter
from datetime import datetime
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
import io

# Map extensions to TYPE_OF_DOCS choices
EXTENSION_TO_DOC_TYPE = {
    ".pdf": 0,
    ".doc": 1,
    ".docx": 1,
    ".xls": 2,
    ".xlsx": 2,
    ".jpg": 3,
    ".jpeg": 3,
    ".png": 3,
    ".gif": 3,
    ".txt": 4,
    ".html": 5,
    ".htm": 5,
    ".eml": 6,
}


def get_dated_storing_folder(base_dir="uploads"):
    """
    Creates and returns the path to a folder inside MEDIA_ROOT/uploads/YYYY-MM-DD
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    storing_folder = os.path.join(settings.MEDIA_ROOT, base_dir, current_date)
    os.makedirs(storing_folder, exist_ok=True)
    return storing_folder


class FileUploadRecordCreateAPIView(CreateAPIView):
    authentication_classes = [OAuth2Authentication]
    # domain restriction permission commented for future use
    # permission_classes = [IsAuthenticated, IsAllowedOrigin]
    permission_classes = [CustomScopePermission]
    queryset = FileUploadRecord.objects.all()
    serializer_class = MultipleFileUploadSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_doc_type(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        return EXTENSION_TO_DOC_TYPE.get(ext, 0)  # Default to PDF (0)

    def get_pdf_page_count(self, file):
        file.seek(0)
        reader = PdfReader(file)
        return len(reader.pages)

    def create_modified_pdf(self, file, max_pages):
        file.seek(0)
        reader = PdfReader(file)
        writer = PdfWriter()

        for i in range(min(len(reader.pages), max_pages)):
            writer.add_page(reader.pages[i])

        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return InMemoryUploadedFile(
            output_stream,
            field_name="modified_file_path",
            name=f"modified_{file.name}",
            content_type="application/pdf",
            size=output_stream.getbuffer().nbytes,
            charset=None,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        files = serializer.validated_data.get("original_file_path")
        if not files:
            return Response(
                {"detail": "No files uploaded."}, status=status.HTTP_400_BAD_REQUEST
            )

        user = None
        if hasattr(request.auth, "application"):
            client_application = request.auth.application
            user = client_application.user
        else:
            return Response(
                {"error": "Client credentials not provided or invalid"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        client_instance = getattr(user, "client_info", None)
        default_max_pages = getattr(client_instance, "default_max_pages", 1)

        results = []

        for file in files:
            file_name = file.name
            doc_type = self.get_doc_type(file_name)
            total_pages = 1
            finalized_pages = 1
            modified_file_path = None

            # Save original file to disk
            storing_folder = get_dated_storing_folder()
            original_file_disk_path = os.path.join(storing_folder, file_name)
            with open(original_file_disk_path, "wb+") as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            original_file_rel_path = os.path.relpath(
                original_file_disk_path, settings.MEDIA_ROOT
            )

            ext = os.path.splitext(file.name)[1].lower()
            if ext == ".pdf":
                try:
                    # Re-open the file from disk for reading page count and modification
                    with open(original_file_disk_path, "rb") as pdf_file:
                        total_pages = self.get_pdf_page_count(pdf_file)
                        finalized_pages = total_pages

                        if total_pages > default_max_pages:
                            configs = ClientAIParsingConfig.objects.filter(
                                client=client_instance
                            )
                            matched_config = (
                                configs.filter(file_pages=total_pages)
                                .order_by("file_pages")
                                .first()
                            )

                            if matched_config:
                                finalized_pages = matched_config.max_final_pages
                            else:
                                finalized_pages = default_max_pages

                            if finalized_pages != total_pages:
                                with open(
                                    original_file_disk_path, "rb"
                                ) as pdf_to_modify:
                                    modified_stream = self.create_modified_pdf(
                                        pdf_to_modify, finalized_pages
                                    )
                                modified_filename = f"modified_{file_name}"
                                modified_path = os.path.join(
                                    storing_folder, modified_filename
                                )
                                with open(modified_path, "wb") as f_out:
                                    f_out.write(modified_stream.read())

                                modified_file_path = os.path.relpath(
                                    modified_path, settings.MEDIA_ROOT
                                )
                except Exception as e:
                    return Response(
                        {"error": f"Could not read PDF: {str(e)}"}, status=400
                    )

            record = FileUploadRecord.objects.create(
                user=user,
                authentication_type="OAuth2",
                endpoint=request.path,
                request_ip=request.META.get("REMOTE_ADDR"),
                request_domain=request.get_host(),
                file_name=file_name,
                doc_type=doc_type,
                total_pages=total_pages,
                finalized_pages=finalized_pages,
            )

            # Assign original_file_path using FileField.save()
            with open(original_file_disk_path, "rb") as orig_file:
                django_file = File(orig_file)
                record.original_file_path.save(file_name, django_file, save=False)

            # Assign modified_file_path if exists
            if modified_file_path:
                with open(
                    os.path.join(settings.MEDIA_ROOT, modified_file_path), "rb"
                ) as mod_file:
                    django_file_mod = File(mod_file)
                    modified_filename = os.path.basename(modified_file_path)
                    record.modified_file_path.save(
                        modified_filename, django_file_mod, save=False
                    )

            record.save()

            results.append(
                {
                    "id": record.id,
                    "file_name": record.file_name,
                    "original_file_path": (
                        record.original_file_path.url
                        if record.original_file_path
                        else None
                    ),
                    "modified_file_path": (
                        record.modified_file_path.url
                        if record.modified_file_path
                        else None
                    ),
                }
            )

        return Response(results, status=status.HTTP_201_CREATED)


upload_view = FileUploadRecordCreateAPIView.as_view()
