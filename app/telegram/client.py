import os

from telethon import TelegramClient
from telethon import connection as telethon_connection

from app.core.config import settings


def _build_telethon_proxy():
    """
    Build proxy tuple for Telethon.
    For mtproxy: (host, port, secret)
    For socks/http: (proxy_type, host, port)
    """
    proxy_type = settings.telegram_proxy_type
    proxy_host = settings.telegram_proxy_host
    proxy_port = settings.telegram_proxy_port

    if not proxy_type or not proxy_host or proxy_port is None:
        return None

    proxy_type_norm = proxy_type.strip().lower()
    port_int = int(proxy_port)

    # MTProto proxy (from tg://proxy?server=...&port=...&secret=...)
    if proxy_type_norm in {"mtproxy", "mtproto", "mtproto_proxy"}:
        proxy_secret = settings.telegram_proxy_secret
        if not proxy_secret:
            return None
        return (proxy_host, port_int, proxy_secret)

    # SOCKS/HTTP proxy tuple format: (proxy_type, host, port)
    return (proxy_type_norm, proxy_host, port_int)


_proxy = _build_telethon_proxy()

_connection = None
if _proxy and isinstance(_proxy, tuple) and len(_proxy) == 3:
    if (settings.telegram_proxy_type or "").strip().lower() in {
        "mtproxy", "mtproto", "mtproto_proxy"
    }:
        mode = (settings.telegram_mt_proxy_mode or "randomized").strip().lower()
        if mode in {"abridged", "abr"}:
            _connection = telethon_connection.ConnectionTcpMTProxyAbridged
        elif mode in {"intermediate", "inter"}:
            _connection = telethon_connection.ConnectionTcpMTProxyIntermediate
        else:
            _connection = telethon_connection.ConnectionTcpMTProxyRandomizedIntermediate


client_kwargs = dict(
    lang_code="ru",
    system_lang_code="ru-RU",
    device_model="Python Server",
    system_version="Windows 10",
    app_version="1.0",
    connection_retries=5,
    proxy=_proxy,
)

# добавляем connection ТОЛЬКО если это класс
if _connection:
    client_kwargs["connection"] = _connection


client = TelegramClient(
    "sessions/user",
    settings.telegram_api_id,
    settings.telegram_api_hash,
    **client_kwargs
)