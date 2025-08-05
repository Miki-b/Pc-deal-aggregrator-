# core/parser/advanced_parser.py

import re

class AgentParser:
    def __init__(self, message: str):
        self.message = message
        self.data = {}

    def parse(self):
        self.extract_processor()
        self.extract_ram()
        self.extract_storage()
        self.extract_graphics()
        self.extract_screen_size()
        self.extract_generation()
        self.extract_price()
        self.extract_contacts()
        return self.data

    def extract_processor(self):
        match = re.search(r"(Ultra|Core)\s*i? ?\d{1,2} ?[A-Z]?\d*", self.message, re.IGNORECASE)
        if match:
            self.data['processor'] = match.group().strip()

    def extract_ram(self):
        match = re.search(r"(\d{2})\s*GB\s*Ram.*?(DDR\d)?\s*(\d{3,4})?MHZ", self.message, re.IGNORECASE)
        if match:
            self.data['ram'] = {
                "size": match.group(1),
                "type": match.group(2),
                "speed": match.group(3)
            }

    def extract_storage(self):
        match = re.search(r"(\d+)\s*(TB|GB)\s*(SSD|HDD)", self.message, re.IGNORECASE)
        if match:
            self.data['storage'] = f"{match.group(1)} {match.group(2)} {match.group(3)}"

    def extract_graphics(self):
        match = re.search(r"(intel\s+Iris|NIVID?IA?.*?Graphics|AMD Radeon)", self.message, re.IGNORECASE)
        if match:
            self.data['graphics'] = match.group().strip()

    def extract_screen_size(self):
        match = re.search(r"(\d{2}\.?\d?)\s*inch", self.message, re.IGNORECASE)
        if match:
            self.data['screen_size'] = match.group(1)

    def extract_generation(self):
        match = re.search(r"(\d{1,2})(st|nd|rd|th)?\s*generation", self.message, re.IGNORECASE)
        if match:
            self.data['generation'] = match.group(1)

    def extract_price(self):
        match = re.search(r"Price\s*[:\-]?\s*([0-9,]+)", self.message, re.IGNORECASE)
        if match:
            self.data['price'] = match.group(1)
        else:
            # fallback: price mentioned without colon
            match_alt = re.search(r"\b([0-9]{5,6})\b", self.message)
            if match_alt:
                self.data['price'] = match_alt.group(1)

    def extract_contacts(self):
        numbers = re.findall(r"09\d{8}", self.message)
        if numbers:
            self.data['contact_numbers'] = numbers
