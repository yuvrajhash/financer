from __future__ import annotations

from kiteconnect import KiteConnect


def login_url(api_key: str) -> str:
    if not api_key:
        raise ValueError("KITE_API_KEY is required")
    return KiteConnect(api_key=api_key).login_url()


def exchange_request_token(api_key: str, api_secret: str, request_token: str) -> dict:
    if not api_key or not api_secret or not request_token:
        raise ValueError("api_key, api_secret and request_token are required")
    kite = KiteConnect(api_key=api_key)
    return kite.generate_session(request_token, api_secret=api_secret)
