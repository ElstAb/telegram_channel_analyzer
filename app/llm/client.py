import asyncio
from litellm import completion

from app.core.config import settings
from app.llm import logger as llm_logger


async def ask_llm(prompt: str):

    # Log outgoing prompt
    llm_logger.log_prompt(prompt)

    provider = (settings.llm_provider or "litellm").strip().lower()

    if provider == "bothub":
        api_key = settings.bothub_api_key or settings.llm_api_key or settings.openai_api_key
        model = settings.bothub_model or settings.llm_model
        api_base = settings.bothub_base_url or settings.llm_base_url
    else:
        api_key = settings.llm_api_key or settings.openai_api_key
        model = settings.llm_model
        api_base = settings.llm_base_url

    if not api_key:
        raise ValueError(
            "LLM api key is not set. Set LLM_API_KEY (or BOTHUB_API_KEY when LLM_PROVIDER=bothub), "
            "or keep OPENAI_API_KEY for backward compatibility."
        )

    if not model:
        raise ValueError("LLM model is not set. Set LLM_MODEL (or BOTHUB_MODEL when LLM_PROVIDER=bothub).")

    last_exc: Exception | None = None

    for attempt in range(3):
        try:
            # Run the blocking HTTP call off the event loop.
            kwargs = {
                "model": model,
                "api_key": api_key,
                "messages": [{"role": "user", "content": prompt}],
            }
            if api_base:
                # For OpenAI-compatible gateways / proxy providers.
                kwargs["api_base"] = api_base

            response = await asyncio.to_thread(completion, **kwargs)
            break
        except Exception as e:
            last_exc = e
            await asyncio.sleep(1.5 * (attempt + 1))
    else:
        raise last_exc  # type: ignore[misc]

    content = response.choices[0].message.content

    # Log incoming response
    llm_logger.log_response(prompt, content, response)

    return content