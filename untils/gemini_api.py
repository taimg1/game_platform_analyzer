from google import genai
from google.generativeai.types import generation_types
from common.app_settings import settings
from typing import Annotated
from fastapi import Depends
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from google.api_core.exceptions import (
    ServiceUnavailable,
    InternalServerError,
    Aborted,
    ResourceExhausted,
    DeadlineExceeded,
)
import re


class GeminiApi:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_API_MODEL

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=20),
        retry=retry_if_exception_type(
            (
                ServiceUnavailable,
                InternalServerError,
                Aborted,
                ResourceExhausted,
                DeadlineExceeded,
            )
        ),
    )
    async def generate_response(self, prompt: str) -> str | None:
        try:
            print("Attempting to generate response with async client...")
            response = await self.client.aio.models.generate_content(
                model=self.model, contents=prompt
            )
            print("Response generated successfully.")
            return response.text
        except (
            ServiceUnavailable,
            InternalServerError,
            Aborted,
            ResourceExhausted,
            DeadlineExceeded,
        ) as e:
            print(f"A retriable error occurred: {e}. Tenacity will handle the retry.")
            raise
        except Exception as e:
            print(
                f"FATAL: Could not get response from Gemini after multiple retries: {e}"
            )
            return None

    def clean_json_markdown(self, text: str) -> str:
        pattern = r"```(?:json)?(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()

    async def generate_file_from_prompt(self, prompt: str) -> dict:
        try:
            print("Generating file from prompt via Gemini...")

            generation_config = generation_types.GenerationConfig(
                response_mime_type="application/pdf"
            )

            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                generation_config=generation_config,
            )

            if response.candidates and response.candidates[0].content.parts:
                generated_file_data = response.candidates[0].content.parts[0].file_data

                return {
                    "uri": generated_file_data.file_uri,
                    "mime_type": generated_file_data.mime_type,
                    "name": prompt.split("filename '")[1].split("'")[0],
                }

            raise RuntimeError("Gemini response did not contain file_data")

        except Exception as e:
            print(f"Failed to generate file from Gemini: {e}")
            raise


GeminiApiDependency = Annotated[GeminiApi, Depends(GeminiApi)]
