from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    telegram_api_id: int
    telegram_api_hash: str

    # Telegram proxy (SOCKS/HTTP or MTProxy)
    telegram_proxy_type: str | None = None  # e.g. socks5, http, mtproxy
    telegram_proxy_host: str | None = None
    telegram_proxy_port: int | None = None

    # MTProto proxy secret (from tg://proxy?...&secret=...)
    telegram_proxy_secret: str | None = None

    database_url: str

    # Backward-compatible OpenAI key (env: OPENAI_API_KEY)
    openai_api_key: str | None = None

    # Unified LLM settings
    llm_provider: str = "litellm"  # set to "bothub" to use BotHub gateway
    llm_model: str = "openai/gpt-4.1-mini"
    llm_api_key: str | None = None
    llm_base_url: str | None = None

    # BotHub (OpenAI-compatible gateway) settings (env: BOTHUB_*)
    bothub_api_key: str | None = None
    bothub_base_url: str | None = None
    bothub_model: str | None = None

    # LLM logging toggle (set in .env as LLM_LOG_ENABLED=1/0)
    llm_log_enabled: bool = True

    # MTProxy connection mode: randomized / intermediate / abridged
    telegram_mt_proxy_mode: str = "randomized"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()