"""Normalize phone numbers for Telegram (E.164, e.g. +251704346312)."""
import re


def normalize_phone(phone: str, country_code: str = "251") -> str:
    """
    Convert local/other formats to international +E.164.

    Examples (Ethiopia):
      0704346312      -> +251704346312
      251704346312    -> +251704346312
      +251704346312   -> +251704346312
    """
    cleaned = re.sub(r"[\s\-()]", "", phone.strip())
    if not cleaned:
        raise ValueError("Phone number is empty")

    if cleaned.startswith("+"):
        return cleaned

    if cleaned.startswith("00"):
        return "+" + cleaned[2:]

    # Local Ethiopian: 07xxxxxxxx or 09xxxxxxxx
    if cleaned.startswith("0") and len(cleaned) == 10 and cleaned[1] in "79":
        return f"+{country_code}{cleaned[1:]}"

    if cleaned.startswith(country_code):
        return "+" + cleaned

    # Bare number without leading 0
    if cleaned.isdigit() and len(cleaned) == 9 and cleaned[0] in "79":
        return f"+{country_code}{cleaned}"

    return "+" + cleaned.lstrip("0")
