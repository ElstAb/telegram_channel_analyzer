from datetime import datetime, timedelta
import asyncio
import os

from app.telegram.client import client
from app.core.timezone import get_timezone


async def load_messages(channel, days):

    tz = get_timezone()

    end = datetime.now(tz)

    start = end - timedelta(days=days)

    # Transient network errors happen (especially on Windows).
    # Retry a few times to reduce "Server closed the connection" failures.
    last_exc: Exception | None = None

    history_limit = int(os.getenv("TELETHON_HISTORY_LIMIT", "10"))

    for attempt in range(3):
        try:
            messages = []

            async for msg in client.iter_messages(channel, limit=history_limit):
                msg_date = msg.date.astimezone(tz)

                if msg_date < start:
                    break

                messages.append(msg)

            return messages
        except (OSError, ConnectionError) as e:
            last_exc = e
            await asyncio.sleep(1.5 * (attempt + 1))

    if last_exc:
        raise last_exc

    return []