from telethon import events
import traceback

from app.telegram.client import client
from app.processing.command_parser import parse_command
from app.processing.normalizers import normalize_channel
from app.db.access import user_has_channel_access
from app.services.analyzer import analyze
from app.db.session import SessionLocal
from app.db.models import User
from app.telegram.response_formatter import (
    format_result_for_telegram,
    split_text_for_telegram,
    to_filelike,
)


@client.on(events.NewMessage)
async def handler(event):

    if not getattr(event, "text", None):
        return

    user_id = event.sender_id
    username = getattr(event.sender, "username", None)

    # Ensure user exists in DB (auto-register)
    db = SessionLocal()

    try:
        user = db.query(User).filter_by(telegram_id=user_id).first()

        if not user:
            user = User(telegram_id=user_id, username=username)
            db.add(user)
            db.commit()
    finally:
        db.close()

    cmd = parse_command(event.text)

    if not cmd:
        return

    channel, days = cmd

    channel = normalize_channel(channel)

    if not user_has_channel_access(user_id, channel):

        await event.reply("Access denied for this channel")

        return

    status = await event.reply("Analyzing... please wait.")

    try:
        result = await analyze(channel, days)
    except Exception as e:
        # Don't crash the bot on transient network issues.
        err_text = f"Error while analyzing: {e}"
        print(err_text)
        traceback.print_exc()
        try:
            await status.edit(err_text)
        except Exception:
            await event.reply(err_text)
        return

    message_text, attachment_bytes, attachment_name = format_result_for_telegram(result)

    # Send formatted message (split into chunks if needed)
    chunks = split_text_for_telegram(message_text)
    try:
        await status.edit(chunks[0])
    except Exception:
        await event.reply(chunks[0])

    for chunk in chunks[1:]:
        await event.reply(chunk)

    # If raw JSON is large, attach it as a file for completeness
    if attachment_bytes and attachment_name:
        await event.reply(file=to_filelike(attachment_bytes, attachment_name))