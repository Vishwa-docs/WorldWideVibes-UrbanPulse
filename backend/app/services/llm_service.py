"""
LLM Service abstraction for UrbanPulse.

Uses Azure OpenAI when configured and falls back to a deterministic template
service for local/demo reliability when credentials are missing.
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


class FallbackLLMService(BaseLLMService):
    """Deterministic fallback text generator used when Azure is unavailable."""

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        del system_prompt, temperature, max_tokens
        summary = prompt.strip().splitlines()[:8]
        body = "\n".join(f"- {line[:180]}" for line in summary if line.strip())
        if not body:
            body = "- No prompt context was provided."
        return (
            "AI fallback mode is active (no Azure credentials). "
            "Here is a deterministic recommendation summary:\n"
            f"{body}\n"
            "- Use the live-refresh actions to improve confidence and freshness."
        )


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

    Raises when required Azure settings are missing (legacy strict behavior).
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


def get_llm_service_safe() -> BaseLLMService:
    """Get Azure service when available, otherwise deterministic fallback."""
    try:
        return get_llm_service()
    except RuntimeError as e:
        logger.warning("%s. Falling back to template LLM.", e)
        return FallbackLLMService()
