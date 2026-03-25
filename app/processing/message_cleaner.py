def _build_author_display(sender, sender_id: int | None) -> str:
    first_name = getattr(sender, "first_name", None) if sender else None
    last_name = getattr(sender, "last_name", None) if sender else None
    username = getattr(sender, "username", None) if sender else None

    name_parts = [p for p in [first_name, last_name] if isinstance(p, str) and p.strip()]
    if name_parts:
        return " ".join(name_parts).strip()

    if isinstance(username, str) and username.strip():
        return f"@{username.strip()}"

    return str(sender_id) if sender_id is not None else "unknown"


def _truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


async def clean_message(msg):
    # Prefer cached sender info from Telethon message if available.
    sender = getattr(msg, "sender", None)
    if sender is None:
        try:
            sender = await msg.get_sender()
        except Exception:
            sender = None

    sender_id = getattr(msg, "sender_id", None)
    message_id = getattr(msg, "id", None)
    reply_to_id = getattr(getattr(msg, "reply_to", None), "reply_to_msg_id", None)

    reply = None
    try:
        # Avoid extra Telegram requests: fetch reply message only if message is actually a reply.
        reply_has_id = reply_to_id is not None or getattr(msg, "reply_to_msg_id", None) is not None
        if reply_has_id:
            replied = await msg.get_reply_message()
            if replied:
                replied_sender = getattr(replied, "sender", None)
                if replied_sender is None:
                    try:
                        replied_sender = await replied.get_sender()
                    except Exception:
                        replied_sender = None

                replied_sender_id = getattr(replied, "sender_id", None)
                reply = {
                    "message_id": getattr(replied, "id", None),
                    "date": replied.date.isoformat() if getattr(replied, "date", None) else None,
                    "author_id": replied_sender_id,
                    "author": _build_author_display(replied_sender, replied_sender_id),
                    "text": _truncate(replied.text or "", 700),
                }
    except Exception:
        reply = None

    return {
        "message_id": message_id,
        "reply_to_id": reply_to_id,
        "date": msg.date.isoformat(),
        "author_id": sender_id,
        "author": _build_author_display(sender, sender_id),
        "text": msg.text or "",
        "reply": reply,
    }