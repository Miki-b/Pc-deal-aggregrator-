from abc import ABC, abstractmethod

class BaseParser(ABC):
    @abstractmethod
    def parse(self, message_text: str) -> dict:
        pass
