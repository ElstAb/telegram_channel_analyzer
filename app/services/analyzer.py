from app.telegram.history_loader import load_messages
from app.processing.message_cleaner import clean_message
from app.processing.markdown_formatter import to_markdown
from app.llm.prompt_builder import build_prompt
from app.llm.client import ask_llm
import asyncio


async def analyze(channel, days):

    messages = await load_messages(channel, days)

    # Safety caps: through proxies Telethon can trigger semaphore timeouts.
    # Reduce number of messages and parallel sender/reply resolution.
    max_messages = 10
    if len(messages) > max_messages:
        messages = messages[:max_messages]

    # Lower parallelism to avoid WinError 121 (use 1 for safest under proxies).
    batch_size = 1
    cleaned = []

    for i in range(0, len(messages), batch_size):
        batch = messages[i:i + batch_size]
        cleaned_batch = await asyncio.gather(*(clean_message(m) for m in batch))
        cleaned.extend(cleaned_batch)

    markdown = to_markdown(cleaned)

    prompt = build_prompt(markdown)

    result = await ask_llm(prompt)

    return result