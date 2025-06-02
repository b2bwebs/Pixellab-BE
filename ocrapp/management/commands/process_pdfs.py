import os
import httpx
from mistralai import Mistral
from django.core.management.base import BaseCommand
from django.conf import settings
from ocrapp.models import FileUploadRecord


class Command(BaseCommand):
    help = "Process uploaded Files and extract data using Mistral API"

    def handle(self, *args, **kwargs):
        client = Mistral(api_key=settings.MISTRAL_API_KEY)
        files = FileUploadRecord.objects.filter(is_ai_processed=False)
        prompt_file_path = os.path.join(settings.BASE_DIR, "format_need.txt")
        with open(prompt_file_path, "r", encoding="utf-8") as file:
            prompt_text = file.read()

        for file_record in files:
            file_path = file_record.original_file_path
            if file_record.total_pages != file_record.finalized_pages:
                file_path = file_record.modified_file_path
            if not os.path.exists(file_path):
                self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
                continue

            self.stdout.write(f"Processing file: {file_path}")
            try:
                # Upload to Mistral
                with open(file_path, "rb") as f:
                    uploaded_file = client.files.upload(
                        file={
                            "file_name": os.path.basename(file_path),
                            "content": f,
                        },
                        purpose="ocr",
                    )

                signed_url = client.files.get_signed_url(file_id=uploaded_file.id)
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"""Extract the following fields from the attached purchase order and return in the given JSON format:\n{prompt_text}""",
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
                    model=model,
                    messages=messages,
                    response_format={"type": "json_object"},
                )
                content = chat_response.choices[0].message.content
                model_used = chat_response.model
                usage = chat_response.usage

                # Extract tokens
                input_tokens = usage.prompt_tokens
                output_tokens = usage.completion_tokens
                total_tokens = usage.total_tokens

                self.stdout.write(self.style.SUCCESS(f"Response: {content}"))

                file_record.ai_uploaded_file_id = uploaded_file.id
                file_record.signed_url = signed_url.url
                file_record.input_tokens = input_tokens
                file_record.output_tokens = output_tokens
                file_record.total_tokens = total_tokens
                file_record.model_used = model_used
                file_record.mistral_response = (
                    content  # already in JSON format (as string)
                )
                file_record.is_ai_processed = True
                file_record.is_batched_call = False
                file_record.save()
            except httpx.HTTPError as e:
                file_record.error_message = f"HTTP error: {str(e)}"
                file_record.is_ai_processed = False
                file_record.save()
                self.stderr.write(self.style.ERROR(f"HTTP error for {file_path}: {e}"))
                continue
            except Exception as e:
                file_record.error_message = f"General error: {str(e)}"
                file_record.is_ai_processed = False
                file_record.save()
                self.stderr.write(
                    self.style.ERROR(f"Error processing {file_path}: {e}")
                )
                continue
