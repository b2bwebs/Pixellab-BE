import os
import httpx
import json
import uuid
from mistralai import Mistral
from django.core.management.base import BaseCommand
from django.conf import settings
from ocrapp.models import FileUploadRecord


class Command(BaseCommand):
    help = "Process uploaded Files and extract data using Mistral API Batch"

    def handle(self, *args, **kwargs):
        client = Mistral(api_key=settings.MISTRAL_API_KEY)
        files = FileUploadRecord.objects.filter(is_ai_processed=False)
        prompt_file_path = os.path.join(settings.BASE_DIR, "format_need.txt")
        with open(prompt_file_path, "r", encoding="utf-8") as file:
            prompt_text = file.read()
        # Step 1: Upload All Files and Get Signed URLs
        file_urls = {}
        for file_record in files:
            file_path = file_record.original_file_path
            if file_record.total_pages != file_record.finalized_pages:
                file_path = file_record.modified_file_path
            if not os.path.exists(file_path):
                self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
                continue
            with open(file_path, "rb") as f:
                uploaded_file = client.files.upload(
                    file={
                        "file_name": os.path.basename(file_path),
                        "content": f,
                    },
                    purpose="ocr",
                )

            signed_url = client.files.get_signed_url(file_id=uploaded_file.id)
            file_urls[file_record.pk] = {
                "file_path": file_path,
                "file_id": uploaded_file.id,
                "signed_url": signed_url.url,
                "record": file_record,
            }
        if not file_urls:
            self.stdout.write("No valid files to process.")
            return
        # Step 2: Create a .jsonl File with Batch Messages
        # Create a unique .jsonl file
        jsonl_filename = f"batch_requests_{uuid.uuid4().hex}.jsonl"
        with open(jsonl_filename, "w") as f:
            for pk, data in file_urls.items():
                message = {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Extract the following fields from the attached purchase order and return in the given JSON format:\n{prompt_text}",
                        },
                        {"type": "document_url", "document_url": data["signed_url"]},
                    ],
                }
                item = {
                    "custom_id": str(pk),
                    "body": {
                        "model": "mistral-large-latest",
                        "messages": [message],
                        "response_format": {"type": "json_object"},
                    },
                }
                f.write(json.dumps(item) + "\n")
        # Step 3: Upload .jsonl File and Submit Batch Job
        # Upload the batch JSONL file
        with open(jsonl_filename, "rb") as f:
            batch_file = client.files.upload(
                file={"file_name": jsonl_filename, "content": f},
                purpose="batch",
            )

        # Submit the batch job
        batch_job = client.batch.jobs.create(
            input_files=[batch_file.id],
            model="mistral-large-latest",  # should match model used in each body
            endpoint="/v1/chat/completions",
        )
        # Step 4: Retrieve Batch Results
        # Wait for job to complete, then get results
        results = client.batch.jobs.results(job_id=batch_job.id)

        # Each result contains the `custom_id` and the model's response
        for result in results:
            pk = int(result.custom_id)
            record = file_urls[pk]["record"]
            response_data = result.response
            try:
                content = response_data["choices"][0]["message"]["content"]
                model_used = response_data.get("model")
                usage = response_data.get("usage", {})
                record.ai_uploaded_file_id = file_urls[pk]["file_id"]
                record.signed_url = file_urls[pk]["signed_url"]
                record.input_tokens = usage.get("prompt_tokens", 0)
                record.output_tokens = usage.get("completion_tokens", 0)
                record.total_tokens = usage.get("total_tokens", 0)
                record.model_used = model_used
                record.mistral_response = content
                record.batch_file_id = batch_job.id
                record.is_ai_processed = True
                record.is_batched_call = True
                record.save()
                print(f"✅ ID {pk} processed.")
            except httpx.HTTPError as e:
                record.error_message = f"HTTP error: {str(e)}"
                record.is_ai_processed = False
                record.save()
                self.stderr.write(
                    self.style.ERROR(
                        f"HTTP error for {file_urls[pk]['file_path']}: {e}"
                    )
                )
                continue
            except Exception as e:
                record.error_message = f"General error: {str(e)}"
                record.is_ai_processed = False
                record.save()
                self.stderr.write(
                    self.style.ERROR(
                        f"Error processing {file_urls[pk]['file_path']}: {e}"
                    )
                )
                continue
