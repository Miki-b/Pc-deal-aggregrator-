import re
from datetime import datetime
from app.parsers.base_parser import BaseParser
from app.agents.ai_agent import AIAgentParser
from app.services.catagorizer import categorize_deal
from app.services.scorer import score_deal

class RegexParser(BaseParser):
    def parse(self, message_text: str) -> dict:
        # Step 1: Use Gemini AI Parser
        ai_parser = AIAgentParser()
        ai_result = ai_parser.parse(message_text)

        # Normalize price if needed
        price = ai_result.get('price')
        try:
            if isinstance(price, str):
                price_cleaned = price.replace(",", "").strip()
                ai_result['price'] = int(price_cleaned)
            elif isinstance(price, (float, int)):
                ai_result['price'] = int(price)
        except:
            ai_result['price'] = None

        return self._normalize(ai_result, message_text)

    def _normalize(self, result: dict, raw: str) -> dict:
        """Ensure all fields exist for compatibility with Deal dataclass."""
        fields = [
            "title", "model", "processor", "generation", "ram", "storage",
            "screen_size", "resolution", "graphics_card", "graphics_memory",
            "battery_life", "condition", "price", "currency", "url", "urls",
            "contact_numbers", "image_path", "raw_message", "timestamp"
        ]
        normalized = {key: result.get(key) for key in fields}
        normalized["raw_message"] = raw
        normalized["timestamp"] = datetime.utcnow()
        normalized["urls"] = normalized.get("urls") or ([normalized["url"]] if normalized.get("url") else [])
        normalized["contact_numbers"] = normalized.get("contact_numbers") or []
        normalized["categories"] = categorize_deal(normalized)
        general_score, category_scores = score_deal(normalized)
        normalized["general_score"] = general_score
        normalized["category_scores"] = category_scores
        return normalized
