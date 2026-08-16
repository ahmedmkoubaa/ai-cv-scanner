import httpx

from domain.ports import LLMPort

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterAdapter:
    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is required when LLM_PROVIDER=openrouter"
            )
        self._api_key = api_key
        self._model = model

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": 0.2,
        }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ai-cv-scanner",
            "X-Title": "AI CV Scanner Backend",
        }

        with httpx.Client(timeout=120.0) as client:
            response = client.post(OPENROUTER_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError("OpenRouter returned no choices")

        content = choices[0].get("message", {}).get("content")
        if not content:
            raise RuntimeError("OpenRouter returned empty content")
        return content


def create_openrouter_adapter(api_key: str, model: str) -> LLMPort:
    return OpenRouterAdapter(api_key=api_key, model=model)
