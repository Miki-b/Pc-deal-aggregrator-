from google import genai
import re
import logging
import json
from app.parsers.base_parser import BaseParser
import traceback

logging.basicConfig(level=logging.DEBUG)

class AIAgentParser(BaseParser):
    def __init__(self):
        self.client = genai.Client()

    def parse(self, message_text: str) -> dict:
        if not message_text.strip():
            return self._fallback(message_text, reason="Empty input")

        prompt = """You are an AI parser designed to extract detailed product specifications from social media posts about laptop sales. Your task is to analyze the provided text and produce a structured JSON object containing the following information.

Extract the following as a valid JSON object (no markdown, no explanation):

- **title**: The main product name, including brand and model (e.g., "HP Spectre x360").
- **model**: The specific model name or number (e.g., "katana 15").
- **processor**: The full processor name (e.g., "Intel® Core™ i7-13650H", "Core i7").
- **generation**: The processor generation, if specified (e.g., "13th generation", "8th generation"). Return null if not explicitly mentioned.
- **ram**: The full RAM specification, including size, type, and speed (e.g., "16GB DDR4 3200MHZ", "DDR5 8GB*2 (4800MHz)").
- **storage**: The full storage specification, including size, type, and interface (e.g., "512 gb ssd", "512GB NVMe PCIe SSD Gen4x4").
- **screen_size**: The screen diagonal measurement in inches (e.g., "15.6 inch").
- **resolution**: The screen resolution (e.g., "4k Resolution", "FHD (1920*1080)").
- **graphics_card**: The name of the dedicated graphics card (e.g., "NVIDIA® GeForce RTX™ 4060 Laptop GPU").
- **graphics_memory**: The size of the dedicated graphics memory (e.g., "8GB GDDR6", "2GB NIVIDA Dedicated Graphics").
- **condition**: The condition of the laptop (e.g., "New arival", "PACKED").
- **battery_life**: The advertised battery life (e.g., "2 hour battery life").
- **price**: A number representing the price. Return null if not specified.
- **currency**: The currency of the price (e.g., "Birr"). Return null if not specified.
- **contact_numbers**: A list of all valid phone numbers found.
- **urls**: A list of all URLs found (e.g., Telegram, website links).
- **raw_message**: The complete, unedited original message text.

If any field is not found, its value should be null. Prioritize detailed information over general information. For instance, if both "16GB Ram" and "16GB Ram DDR4 3200MHZ" are present, extract the latter for the `ram` field. Ignore any formatting characters like emojis, arrows, or checkboxes."""  # your full prompt here

        try:
            full_prompt = f"{prompt}\n\nMessage:\n{message_text}"
            logging.debug("Sending prompt to Gemini:\n%s", full_prompt)

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt
            )
            raw_output = response.text.strip()
            logging.debug("Gemini raw output:\n%s", raw_output)

            json_text = self._extract_json(raw_output)
            structured = json.loads(json_text)

            return self._normalize_fields(structured, message_text)

        except Exception as e:
            logging.error(f"Gemini parsing failed: {e}")
            traceback.print_exc()
            return self._fallback(message_text, reason="Exception during parsing")

    def _extract_json(self, text: str) -> str:
        text = text.strip("`").strip()
        start = text.find('{')
        end = text.rfind('}')
        if start == -1 or end == -1 or end <= start:
            return text
        return text[start:end+1]

    def _normalize_fields(self, structured: dict, raw: str) -> dict:
        defaults = {
            "title": None, "model": None, "processor": None, "generation": None,
            "ram": None, "storage": None, "screen_size": None, "resolution": None,
            "graphics_card": None, "graphics_memory": None, "condition": None,
            "battery_life": None, "price": None, "currency": None,
            "contact_numbers": [], "urls": [], "raw_message": raw
        }

        for key, default_val in defaults.items():
            if key not in structured or structured[key] is None:
                structured[key] = default_val

        if isinstance(structured.get("urls"), str):
            structured["urls"] = [structured["urls"]]

        if "phone_numbers" in structured:
            structured["contact_numbers"] = structured.pop("phone_numbers")

        return structured

    def _fallback(self, raw: str, reason: str = "unknown") -> dict:
        logging.warning(f"AI fallback triggered due to: {reason}")
        return {
            "title": "AI Fallback: " + raw[:50],
            "model": None,
            "processor": None,
            "generation": None,
            "ram": None,
            "storage": None,
            "screen_size": None,
            "resolution": None,
            "graphics_card": None,
            "graphics_memory": None,
            "condition": None,
            "battery_life": None,
            "price": None,
            "currency": None,
            "contact_numbers": [],
            "urls": [],
            "raw_message": raw
        }
