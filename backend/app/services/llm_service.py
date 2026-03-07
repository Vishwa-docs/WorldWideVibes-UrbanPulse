"""
LLM Service abstraction for UrbanPulse.
Uses Azure OpenAI (AsyncAzureOpenAI) as the sole LLM provider.
"""
import logging
from abc import ABC, abstractmethod

from openai import AsyncAzureOpenAI

logger = logging.getLogger(__name__)


class BaseLLMService(ABC):
    """Abstract base for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        pass


class AzureOpenAIService(BaseLLMService):
    """Azure OpenAI integration via the openai Python SDK."""

    def __init__(
        self,
        endpoint: str,
        api_key: str,
        deployment: str,
        api_version: str,
    ):
        self.deployment = deployment
        self.client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error("Azure OpenAI request failed: %s", e)
            raise


def get_llm_service() -> BaseLLMService:
    """Factory function to get the Azure OpenAI LLM service.

    Raises ``RuntimeError`` when required Azure OpenAI configuration values
    are missing so the error surfaces immediately on startup.
    """
    from app.config import get_settings

    settings = get_settings()

    missing = []
    if not getattr(settings, "azure_openai_endpoint", None):
        missing.append("AZURE_OPENAI_ENDPOINT")
    if not getattr(settings, "azure_openai_api_key", None):
        missing.append("AZURE_OPENAI_API_KEY")
    if not getattr(settings, "azure_openai_deployment", None):
        missing.append("AZURE_OPENAI_DEPLOYMENT")
    if not getattr(settings, "azure_openai_api_version", None):
        missing.append("AZURE_OPENAI_API_VERSION")

    if missing:
        raise RuntimeError(
            "Azure OpenAI is not configured. "
            f"Missing environment variable(s): {', '.join(missing)}"
        )

    return AzureOpenAIService(
        endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_api_key,
        deployment=settings.azure_openai_deployment,
        api_version=settings.azure_openai_api_version,
    )
