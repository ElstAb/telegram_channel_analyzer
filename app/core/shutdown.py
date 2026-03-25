import asyncio
from app.telegram.client import client


def shutdown_app():

    print("\nStopping Telegram client...")

    # Use the Telethon client's existing event loop and
    # schedule a disconnect from the console thread.
    loop = client.loop

    future = asyncio.run_coroutine_threadsafe(client.disconnect(), loop)
    future.result()

    print("Session closed")
    print("Application stopped")