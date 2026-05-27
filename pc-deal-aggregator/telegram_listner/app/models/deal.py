"""
Pydantic models for Deal API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class DealBase(BaseModel):
    """Base deal model with common fields"""
    title: Optional[str] = None
    model: Optional[str] = None
    processor: Optional[str] = None
    generation: Optional[str] = None
    ram: Optional[str] = None
    storage: Optional[str] = None
    screen_size: Optional[str] = Field(None, alias="screenSize")
    resolution: Optional[str] = None
    graphics_card: Optional[str] = Field(None, alias="graphicsCard")
    graphics_memory: Optional[str] = Field(None, alias="graphicsMemory")
    battery_life: Optional[str] = Field(None, alias="batteryLife")
    condition: Optional[str] = None
    price: Optional[int] = None
    currency: Optional[str] = "Birr"
    contact_numbers: List[str] = Field(default_factory=list, alias="contactNumbers")
    urls: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    general_score: int = Field(0, alias="generalScore")
    category_scores: Dict[str, int] = Field(default_factory=dict, alias="categoryScores")

    class Config:
        populate_by_name = True


class DealCreate(DealBase):
    """Model for creating a new deal"""
    raw_message: str = Field(..., alias="rawMessage")
    image_path: Optional[str] = Field(None, alias="imagePath")
    channel_id: Optional[str] = Field(None, alias="channelId")
    message_id: Optional[str] = Field(None, alias="messageId")
    telegram_url: Optional[str] = Field(None, alias="telegramUrl")


class DealResponse(DealBase):
    """Model for deal API responses"""
    id: str
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    raw_message: str = Field(..., alias="rawMessage")
    image_path: Optional[str] = Field(None, alias="imagePath")
    channel_id: Optional[str] = Field(None, alias="channelId")
    message_id: Optional[str] = Field(None, alias="messageId")
    telegram_url: Optional[str] = Field(None, alias="telegramUrl")

    class Config:
        from_attributes = True
        populate_by_name = True


class DealFilter(BaseModel):
    """Model for filtering deals"""
    min_price: Optional[int] = Field(None, alias="minPrice")
    max_price: Optional[int] = Field(None, alias="maxPrice")
    categories: Optional[List[str]] = None
    processor: Optional[str] = None
    min_ram: Optional[int] = Field(None, alias="minRam")
    min_storage: Optional[int] = Field(None, alias="minStorage")
    graphics_card: Optional[str] = Field(None, alias="graphicsCard")
    condition: Optional[str] = None
    min_score: Optional[int] = Field(None, alias="minScore")
    search: Optional[str] = None  # Full-text search in title/model
    
    class Config:
        populate_by_name = True


class DealStats(BaseModel):
    """Model for deal statistics"""
    total_deals: int = Field(..., alias="totalDeals")
    avg_price: Optional[float] = Field(None, alias="avgPrice")
    min_price: Optional[int] = Field(None, alias="minPrice")
    max_price: Optional[int] = Field(None, alias="maxPrice")
    categories_count: Dict[str, int] = Field(..., alias="categoriesCount")
    brands_count: Dict[str, int] = Field(..., alias="brandsCount")
    
    class Config:
        populate_by_name = True


class PaginatedDeals(BaseModel):
    """Model for paginated deal responses"""
    deals: List[DealResponse]
    total: int
    page: int
    page_size: int = Field(..., alias="pageSize")
    total_pages: int = Field(..., alias="totalPages")
    
    class Config:
        populate_by_name = True
