"""Handoff Core Library — LLM Fallback Wrapper.

Centralizes generation calls to the Gemini API with automatic exception
handling and fallback routing to ensure resilience against rate limits
or transient model unavailabilities.
"""

from google import genai
from google.genai.types import GenerateContentConfig
from google.api_core import exceptions

from core.config import config


async def generate_content_with_fallback(
    contents: list | str,
    gen_config: GenerateContentConfig,
    primary_model: str = config.gen_model,
    fallback_model: str = config.fallback_model,
) -> str | None:
    """Generate content from Gemini, gracefully falling back on errors.

    If the primary model call fails (e.g. ResourceExhausted rate limit),
    this wrapper catches the exception and immediately retries against
    the designated fallback model (usually a faster/cheaper flash model).

    Args:
        contents: The prompt payload (text or Part array).
        gen_config: The generation settings (temperature, schema, etc).
        primary_model: The ideal model to use (default: 3.1-pro-preview).
        fallback_model: The safety model to use (default: 3.0-flash).

    Returns:
        The generated text string, or None if both models fail.
    """
    client = genai.Client(api_key=config.gemini_api_key)

    try:
        response = await client.aio.models.generate_content(
            model=primary_model,
            contents=contents,
            config=gen_config,
        )
        return response.text.strip()
    except Exception as primary_error:
        print(f"[LLM] Primary model ({primary_model}) failed: {primary_error}")
        print(f"[LLM] Initiating fallback sequence to {fallback_model}...")
        
        try:
            fallback_response = await client.aio.models.generate_content(
                model=fallback_model,
                contents=contents,
                config=gen_config,
            )
            return fallback_response.text.strip()
        except Exception as fallback_error:
            print(f"[LLM] Fatal: Fallback model also failed: {fallback_error}")
            return None
