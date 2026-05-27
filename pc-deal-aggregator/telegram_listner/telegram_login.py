"""
One-time Telegram login. Run this in your terminal before start_listener.py.

    python telegram_login.py
"""
import asyncio
import sys

from telethon.errors import PhoneNumberInvalidError

from app.core.config import settings
from app.core.phone import normalize_phone
from app.services.telegram_service import telegram_service


def _resolve_phone() -> str:
    if settings.TELEGRAM_PHONE:
        return normalize_phone(settings.TELEGRAM_PHONE)

    raw = input(
        "Phone (international format, e.g. +251704346312): "
    ).strip()
    return normalize_phone(raw)


async def main() -> None:
    print("Telegram login — you will receive a code in the Telegram app.")
    print(f"Session file: {settings.TELEGRAM_SESSION_NAME}.session")
    print("Tip: local 0704346312 becomes +251704346312 automatically.\n")

    try:
        phone = _resolve_phone()
        print(f"Using phone: {phone}")
        await telegram_service.client.start(phone=phone)
    except PhoneNumberInvalidError:
        print(
            "\n[FAIL] Invalid phone number for Telegram.\n"
            "Use international format with country code, e.g. +251704346312\n"
            "Not: 0704346312 alone, and not 25170704346312 (too many digits).\n"
            "Or set TELEGRAM_PHONE=+251704346312 in your .env file."
        )
        sys.exit(1)

    await telegram_service.client.disconnect()
    print("[OK] Logged in. You can now run: python start_listener.py")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
