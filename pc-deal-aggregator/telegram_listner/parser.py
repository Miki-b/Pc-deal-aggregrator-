import re

def parse_message(message_text):
    """
    Extracts useful info from a Telegram message about a PC/laptop/tech deal.
    This is a basic parser — you can improve it later with more logic or AI.
    """

    # Extract price (ETB or numbers like 45,000)
    price_match = re.search(r'(\d{1,3}(,\d{3})+|\d+)\s*(ETB|Birr|ብር)?', message_text, re.IGNORECASE)
    price = price_match.group(1).replace(',', '') if price_match else None

    # Extract first URL if available
    url_match = re.search(r'(https?://\S+)', message_text)
    url = url_match.group(1) if url_match else None

    # Example: title from first line or bold/ALLCAPS text
    lines = message_text.strip().split('\n')
    title = lines[0][:100] if lines else "No Title"

    # Basic data object
    return {
        "title": title,
        "price": int(price) if price and price.isdigit() else None,
        "url": url,
        "raw_message": message_text
    }
