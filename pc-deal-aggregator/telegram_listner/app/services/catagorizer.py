from typing import List
import re

def categorize_deal(deal: dict) -> List[str]:
    categories = []
    title = (deal.get("title") or "").lower()
    desc = (deal.get("raw_message") or "").lower()

    combined_text = f"{title} {desc}"

    # Use Case Categories
    if any(term in combined_text for term in ["gaming", "rtx", "gtx", "1650", "2060", "3060", "fps"]):
        categories.append("Gaming")
    if any(term in combined_text for term in ["developer", "programming", "vs code", "coding"]):
        categories.append("Programming")
    if any(term in combined_text for term in ["graphic", "photoshop", "illustrator", "design", "adobe"]):
        categories.append("Graphic Design")
    if "workstation" in combined_text:
        categories.append("Workstation")
    if "student" in combined_text:
        categories.append("Student Laptop")
    if "office" in combined_text:
        categories.append("Office Use")
    if "edit" in combined_text or "video" in combined_text:
        categories.append("Video Editing")

    # Price-based Categories
    price = deal.get("price")
    if isinstance(price, int):
        if price < 30000:
            categories.append("Budget")
        elif 30000 <= price <= 60000:
            categories.append("Mid-range")
        else:
            categories.append("Premium")

    # Brand Categories
    brands = ["hp", "dell", "lenovo", "apple", "acer", "asus", "microsoft"]
    for brand in brands:
        if brand in combined_text:
            categories.append(brand.capitalize())

    # Form Factor
    if "touch" in combined_text:
        categories.append("Touchscreen")
    if "ultrabook" in combined_text or ("thin" in combined_text and "light" in combined_text):
        categories.append("Ultrabook")
    if "2 in 1" in combined_text or "2-in-1" in combined_text:
        categories.append("2-in-1")
    if "desktop replacement" in combined_text:
        categories.append("Desktop Replacement")

    return list(set(categories))  # Remove duplicates
