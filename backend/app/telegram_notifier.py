import hashlib
from pydoc import text
import token
import requests
from typing import Optional
from .config import settings


class TelegramSettings:
    """Settings class for Telegram configuration"""
    def __init__(self, enabled: bool = True):
        self.TELEGRAM_NOTIFICATION_ENABLED = enabled


class Telegram:
    def __init__(self, token: str, chat_id: str, settings_override: Optional[TelegramSettings] = None):
        self.base = f"https://api.telegram.org/bot{token}"
        self.chat_id = chat_id
        
        # Use override settings if provided, otherwise use global settings
        if settings_override is not None:
            self.enabled = bool(settings_override.TELEGRAM_NOTIFICATION_ENABLED)
        else:
            self.enabled = bool(settings.TELEGRAM_NOTIFICATION_ENABLED)

    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def send(self, text: str) -> str:
        if not self.enabled:
            return self._hash(text)
        
        try:
            url = f"{self.base}/sendMessage"
            r = requests.post(url, json={"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"})
            r.raise_for_status()
        except Exception as e:
            print(f"Failed to send Telegram notification: {e}")
        
        return self._hash(text)