from typing import Protocol


class LLMAdapter(Protocol):
    def generate(self, prompt: str, *, system: str | None = None) -> str:
        """Generate text from the LLM given a user prompt and optional system instruction."""
        ...
