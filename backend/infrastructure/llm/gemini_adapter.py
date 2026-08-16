from google import genai
from google.genai import types

from domain.ports import LLMPort


class GeminiAdapter:
    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required when LLM_PROVIDER=gemini")
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        config = types.GenerateContentConfig(temperature=0.2)
        if system:
            config.system_instruction = system

        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=config,
        )

        text = response.text
        if not text:
            raise RuntimeError("Gemini returned an empty response")
        return text


def create_gemini_adapter(api_key: str, model: str) -> LLMPort:
    return GeminiAdapter(api_key=api_key, model=model)
