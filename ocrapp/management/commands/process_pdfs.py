from django.core.management.base import BaseCommand
from django.conf import settings
from ocrapp.models import FileUploadRecord
from mistralai import Mistral
import os


class Command(BaseCommand):
    help = "Process uploaded PDFs and extract data using Mistral API"

    def handle(self, *args, **kwargs):
        client = Mistral(api_key=settings.MISTRAL_API_KEY)
        files = FileUploadRecord.objects.filter(is_processed=False)

        for file_record in files:
            file_path = file_record.file.path

            self.stdout.write(f"Processing file: {file_path}")

            # Upload to Mistral
            with open(file_path, "rb") as f:
                uploaded_pdf = client.files.upload(
                    file={
                        "file_name": os.path.basename(file_path),
                        "content": f,
                    },
                    purpose="ocr",
                )

            signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)

            prompt = """ JSON format instruction here"""

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""Extract the following fields from the attached purchase order and return in the given JSON format:\n{prompt}""",
                        },
                        {
                            "type": "document_url",
                            "document_url": signed_url.url,
                        },
                    ],
                }
            ]

            model = "mistral-large-latest"

            chat_response = client.chat.complete(
                model=model, messages=messages, response_format={"type": "json_object"}
            )
            content = chat_response.choices[0].message.content
            model_used = chat_response.model
            usage = chat_response.usage

            # Extract tokens
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens

            self.stdout.write(self.style.SUCCESS(f"Response: {content}"))

            file_record.input_tokens = input_tokens
            file_record.output_tokens = output_tokens
            file_record.total_tokens = total_tokens
            file_record.model_used = model_used
            file_record.mistral_response = content  # already in JSON format (as string)
            file_record.is_processed = True
            file_record.save()
