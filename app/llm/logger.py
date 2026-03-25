import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from app.core.config import settings


# Base directory for LLM logs (relative to project root)
LOG_BASE_DIR = Path("logs") / "llm"


def _ensure_dir(subdir: str) -> Path:

    path = LOG_BASE_DIR / subdir
    path.mkdir(parents=True, exist_ok=True)
    return path


def _timestamp() -> str:

    return datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")


def log_prompt(prompt: str) -> None:

    if not settings.llm_log_enabled:
        return

    dir_path = _ensure_dir("prompts")
    ts = _timestamp()

    payload: Dict[str, Any] = {
        "timestamp_utc": ts,
        "prompt": prompt,
    }

    file_path = dir_path / f"{ts}.json"
    file_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def log_response(prompt: str, response_content: str, raw_response: Any) -> None:

    if not settings.llm_log_enabled:
        return

    dir_path = _ensure_dir("responses")
    ts = _timestamp()

    # We don't know exact type of raw_response, so best effort to serialize
    try:
        raw = raw_response.model_dump()  # pydantic / litellm objects often support this
    except Exception:

        try:
            raw = json.loads(raw_response.json())  # type: ignore[attr-defined]
        except Exception:
            raw = str(raw_response)

    payload: Dict[str, Any] = {
        "timestamp_utc": ts,
        "prompt": prompt,
        "response": response_content,
        "raw_response": raw,
    }

    file_path = dir_path / f"{ts}.json"
    file_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

