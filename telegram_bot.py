import os
import requests


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def enviar_telegram(mensaje):
    if not TELEGRAM_TOKEN:
        raise RuntimeError("Falta TELEGRAM_TOKEN en GitHub Secrets")

    if not TELEGRAM_CHAT_ID:
        raise RuntimeError("Falta TELEGRAM_CHAT_ID en GitHub Secrets")

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    r = requests.post(
        url,
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": mensaje,
            "disable_web_page_preview": True,
        },
        timeout=30,
    )

    if not r.ok:
        raise RuntimeError(f"Telegram error {r.status_code}: {r.text}")

    return True
