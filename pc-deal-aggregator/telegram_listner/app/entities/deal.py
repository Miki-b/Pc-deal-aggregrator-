from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Deal:
    title: str
    model: Optional[str] = None
    processor: Optional[str] = None
    generation: Optional[str] = None
    ram: Optional[str] = None
    storage: Optional[str] = None
    screen_size: Optional[str] = None
    resolution: Optional[str] = None
    graphics_card: Optional[str] = None
    graphics_memory: Optional[str] = None
    condition: Optional[str] = None
    battery_life: Optional[str] = None
    price: Optional[int] = None
    currency: Optional[str] = None
    contact_numbers: Optional[List[str]] = None
    urls: Optional[List[str]] = None
    url: Optional[str] = None  # keep this if you want single main url
    image_path: Optional[str] = None
    raw_message: str = ""
    timestamp: datetime = None
