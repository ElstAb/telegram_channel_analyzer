import io
import json
from typing import Any, Dict, List, Optional, Tuple


TELEGRAM_TEXT_LIMIT = 4096


def _safe_json_loads(text: str) -> Optional[Dict[str, Any]]:
    cleaned = text.strip()
    # Some models may wrap JSON into code fences. Strip them for robustness.
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        # After stripping, it may still start with "json\n"
        cleaned = cleaned.lstrip()
        if cleaned.lower().startswith("json"):
            # remove leading "json" token + possible newline
            cleaned = cleaned[4:].lstrip()

    try:
        value = json.loads(cleaned)
    except Exception:
        # Try extracting the first JSON object from the text.
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            try:
                value = json.loads(cleaned[start:end + 1])
            except Exception:
                return None
        else:
            return None
    if not isinstance(value, dict):
        return None
    return value


def _truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def _format_agenda(data: Dict[str, Any]) -> str:
    chat_summary = data.get("chat_summary") or {}
    agenda = data.get("agenda") or []

    if not isinstance(chat_summary, dict):
        chat_summary = {}
    if not isinstance(agenda, list):
        agenda = []

    summary_text = chat_summary.get("text") if isinstance(chat_summary.get("text"), str) else ""
    parts: List[str] = ["Agenda"]
    if summary_text.strip():
        parts.append(summary_text.strip())

    blocks: List[str] = []
    for i, item in enumerate(agenda):
        if not isinstance(item, dict):
            continue
        question = item.get("question") if isinstance(item.get("question"), str) else ""
        asked_by = item.get("asked_by") if isinstance(item.get("asked_by"), str) else ""
        answers = item.get("answers") if isinstance(item.get("answers"), list) else []

        q_line = _truncate(question.strip(), 500) if question else "(вопрос не распознан)"
        ab_line = asked_by.strip() if asked_by else "unknown"

        blocks.append(f"{i+1}. {q_line}\nAsked by: {ab_line}")

        if not answers:
            blocks.append("- Answers: (none)")
            continue

        ans_lines: List[str] = []
        for ans in answers:
            if not isinstance(ans, dict):
                continue
            answer_text = ans.get("answer") if isinstance(ans.get("answer"), str) else ""
            answered_by = ans.get("answered_by") if isinstance(ans.get("answered_by"), str) else ""

            answer_part = _truncate(answer_text.strip(), 400) if answer_text else "(ответ пустой)"
            answered_by_part = answered_by.strip() if answered_by else "unknown"
            ans_lines.append(f"- {answer_part} (by {answered_by_part})")

        if ans_lines:
            blocks.append("Answers:\n" + "\n".join(ans_lines))

    if blocks:
        parts.append("\n\n".join(blocks))

    return "\n\n".join(parts).strip()


def format_result_for_telegram(llm_result: str) -> Tuple[str, Optional[bytes], str]:
    """
    Returns:
      - message_text: text to send (may be truncated/split by caller)
      - attachment_bytes: optional JSON bytes to send as a file (when too large)
      - attachment_name: suggested filename when attachment_bytes is provided
    """
    data = _safe_json_loads(llm_result)

    if not data:
        # Fallback: return raw text (might be JSON-ish or an error)
        return llm_result, None, ""

    # Old format: telegram_ready_message
    ready = data.get("telegram_ready_message") if isinstance(data, dict) else None
    if isinstance(ready, dict):
        title = ready.get("title") if isinstance(ready.get("title"), str) else "Channel Summary"
        summary = ready.get("summary") if isinstance(ready.get("summary"), str) else ""
        bullet_points = ready.get("bullet_points") if isinstance(ready.get("bullet_points"), list) else []

        bullets: List[str] = []
        for b in bullet_points:
            if isinstance(b, str) and b.strip():
                bullets.append(b.strip())

        parts: List[str] = [f"{title}"]
        if summary.strip():
            parts.append(summary.strip())
        if bullets:
            parts.append("\n".join([f"- {b}" for b in bullets]))

        message_text = "\n\n".join(parts).strip()

        # If message is huge, prefer attaching raw JSON as file too.
        attachment_bytes = None
        attachment_name = ""
        if len(llm_result) > TELEGRAM_TEXT_LIMIT:
            attachment_bytes = llm_result.encode("utf-8")
            attachment_name = "llm_response.json"

        return message_text, attachment_bytes, attachment_name

    # New format: chat_summary + agenda
    if "chat_summary" in data and "agenda" in data:
        message_text = _format_agenda(data)

        attachment_bytes = None
        attachment_name = ""
        if len(llm_result) > TELEGRAM_TEXT_LIMIT:
            attachment_bytes = llm_result.encode("utf-8")
            attachment_name = "llm_response.json"

        return message_text, attachment_bytes, attachment_name

    # Fallback: return raw text
    return llm_result, None, ""


def split_text_for_telegram(text: str, limit: int = TELEGRAM_TEXT_LIMIT) -> List[str]:
    if len(text) <= limit:
        return [text]

    chunks: List[str] = []
    remaining = text
    while len(remaining) > limit:
        cut = remaining.rfind("\n", 0, limit)
        if cut <= 0:
            cut = limit
        chunks.append(remaining[:cut].rstrip())
        remaining = remaining[cut:].lstrip()
    if remaining:
        chunks.append(remaining)
    return chunks


def to_filelike(data: bytes, filename: str) -> io.BytesIO:
    bio = io.BytesIO(data)
    bio.name = filename
    return bio

