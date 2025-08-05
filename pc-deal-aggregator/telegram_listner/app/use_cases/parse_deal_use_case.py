from app.parsers.regex_parser import RegexParser
from app.agents.ai_agent import AIAgentParser

class ParseDealUseCase:
    def __init__(self):
        self.regex_parser = RegexParser()
        self.ai_agent_parser = AIAgentParser()

    def parse(self, message_text: str) -> dict:
        # Try regex parser first
        result = self.regex_parser.parse(message_text)

        # If regex didn't find price or title, fallback to AI agent
        if not result.get("price") or not result.get("title"):
            result = self.ai_agent_parser.parse(message_text)

        return result
