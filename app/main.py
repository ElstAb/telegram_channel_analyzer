import threading

from app.telegram.client import client
import app.telegram.handlers

from app.console.menu import start_console


def run_console():
    start_console()


async def main():
    # Telethon prompts here on first login (phone / code); no output before start() is confusing.
    print("Подключение к Telegram…", flush=True)
    print(
        "Если сессии ещё нет, здесь же запросят телефон и код из приложения Telegram.",
        flush=True,
    )

    await client.start()

    console_thread = threading.Thread(
        target=run_console,
        daemon=True
    )

    console_thread.start()

    print("Telegram-клиент запущен. Меню администратора — в этой же консоли.", flush=True)

    await client.run_until_disconnected()


if __name__ == "__main__":
    # Не используем `with client:`: в Telethon __enter__ вызывает start() до тела блока,
    # поэтому print выше не успевали показаться до запроса телефона.
    try:
        client.loop.run_until_complete(main())
    finally:
        client.disconnect()