from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict], options: dict | None = None) -> str:
        """Send messages to LLM and return response text."""
        ...
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider is reachable."""
        ...
