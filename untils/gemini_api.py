from google import genai
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


class GeminiApi:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_API_MODEL

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10),
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
    async def generate_response(self, prompt: str):
        print("Attempting to generate response...")
        response = self.client.models.generate_content(
            model=self.model, contents=prompt
        )
        return response.text


GeminiApiDependency = Annotated[GeminiApi, Depends(GeminiApi)]
