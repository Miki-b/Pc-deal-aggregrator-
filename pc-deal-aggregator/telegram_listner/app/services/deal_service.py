"""
Business logic for deal operations
"""
from typing import List, Optional, Dict, Any
from prisma import Prisma
from prisma.fields import Json
from prisma.models import Deal
from app.models.deal import DealFilter, DealStats
import re


class DealService:
    """Service for managing deals"""
    
    def __init__(self, db: Prisma):
        self.db = db
    
    async def deal_exists(self, channel_id: str, message_id: str) -> bool:
        """Check if this Telegram message was already saved."""
        existing = await self.db.deal.find_first(
            where={"channelId": channel_id, "messageId": message_id},
        )
        return existing is not None

    async def create_deal(self, deal_data: Dict[str, Any]) -> Deal:
        """Create a new deal in the database"""
        channel_id = deal_data.get("channel_id")
        message_id = deal_data.get("message_id")
        if channel_id and message_id:
            if await self.deal_exists(channel_id, message_id):
                raise ValueError("duplicate")

        # Convert snake_case to camelCase for Prisma
        prisma_data = {
            "title": deal_data.get("title"),
            "model": deal_data.get("model"),
            "rawMessage": deal_data.get("raw_message", ""),
            "imagePath": deal_data.get("image_path"),
            "processor": deal_data.get("processor"),
            "generation": deal_data.get("generation"),
            "ram": deal_data.get("ram"),
            "storage": deal_data.get("storage"),
            "screenSize": deal_data.get("screen_size"),
            "resolution": deal_data.get("resolution"),
            "graphicsCard": deal_data.get("graphics_card"),
            "graphicsMemory": deal_data.get("graphics_memory"),
            "batteryLife": deal_data.get("battery_life"),
            "condition": deal_data.get("condition"),
            "price": deal_data.get("price"),
            "currency": deal_data.get("currency", "Birr"),
            "contactNumbers": deal_data.get("contact_numbers", []),
            "urls": deal_data.get("urls", []),
            "categories": deal_data.get("categories", []),
            "generalScore": deal_data.get("general_score", 0),
            "categoryScores": Json(deal_data.get("category_scores") or {}),
            "channelId": channel_id,
            "messageId": message_id,
            "postedAt": deal_data.get("posted_at"),
            "telegramUrl": deal_data.get("telegram_url"),
        }
        
        deal = await self.db.deal.create(data=prisma_data)
        return deal
    
    async def get_deal_by_id(self, deal_id: str) -> Optional[Deal]:
        """Get a deal by ID"""
        return await self.db.deal.find_unique(where={"id": deal_id})
    
    async def get_deals(
        self,
        skip: int = 0,
        limit: int = 50,
        filters: Optional[DealFilter] = None,
        sort_by: str = "createdAt",
        sort_order: str = "desc"
    ) -> tuple[List[Deal], int]:
        """
        Get deals with pagination and filtering
        Returns: (deals, total_count)
        """
        where_clause = self._build_where_clause(filters)
        
        # Build order by
        order = {sort_by: sort_order}
        
        # Get deals and total count
        deals = await self.db.deal.find_many(
            where=where_clause,
            skip=skip,
            take=limit,
            order=order
        )
        
        total = await self.db.deal.count(where=where_clause)
        
        return deals, total
    
    async def get_deal_stats(self, filters: Optional[DealFilter] = None) -> DealStats:
        """Get statistics about deals"""
        where_clause = self._build_where_clause(filters)
        
        # Get total count
        total = await self.db.deal.count(where=where_clause)
        
        # Get all deals for stats calculation (could be optimized with aggregations)
        deals = await self.db.deal.find_many(where=where_clause)
        
        # Calculate stats
        prices = [d.price for d in deals if d.price is not None]
        avg_price = sum(prices) / len(prices) if prices else None
        min_price = min(prices) if prices else None
        max_price = max(prices) if prices else None
        
        # Count categories
        categories_count: Dict[str, int] = {}
        for deal in deals:
            for category in deal.categories:
                categories_count[category] = categories_count.get(category, 0) + 1
        
        # Count brands (extract from title)
        brands_count: Dict[str, int] = {}
        for deal in deals:
            if deal.title:
                # Extract brand (first word typically)
                brand = deal.title.split()[0] if deal.title else None
                if brand:
                    brands_count[brand] = brands_count.get(brand, 0) + 1
        
        return DealStats(
            totalDeals=total,
            avgPrice=avg_price,
            minPrice=min_price,
            maxPrice=max_price,
            categoriesCount=categories_count,
            brandsCount=brands_count
        )
    
    async def delete_deal(self, deal_id: str) -> bool:
        """Delete a deal by ID"""
        try:
            await self.db.deal.delete(where={"id": deal_id})
            return True
        except Exception:
            return False
    
    async def update_deal(self, deal_id: str, update_data: Dict[str, Any]) -> Optional[Deal]:
        """Update a deal"""
        try:
            deal = await self.db.deal.update(
                where={"id": deal_id},
                data=update_data
            )
            return deal
        except Exception:
            return None
    
    def _build_where_clause(self, filters: Optional[DealFilter]) -> Dict[str, Any]:
        """Build Prisma where clause from filters"""
        if not filters:
            return {}
        
        where: Dict[str, Any] = {}
        
        # Price range
        if filters.min_price is not None or filters.max_price is not None:
            where["price"] = {}
            if filters.min_price is not None:
                where["price"]["gte"] = filters.min_price
            if filters.max_price is not None:
                where["price"]["lte"] = filters.max_price
        
        # Categories (any match)
        if filters.categories:
            where["categories"] = {"hasSome": filters.categories}
        
        # Processor (contains)
        if filters.processor:
            where["processor"] = {"contains": filters.processor, "mode": "insensitive"}
        
        # Graphics card (contains)
        if filters.graphics_card:
            where["graphicsCard"] = {"contains": filters.graphics_card, "mode": "insensitive"}
        
        # Condition (exact match)
        if filters.condition:
            where["condition"] = {"contains": filters.condition, "mode": "insensitive"}
        
        # Minimum score
        if filters.min_score is not None:
            where["generalScore"] = {"gte": filters.min_score}
        
        # Search in title/model
        if filters.search:
            where["OR"] = [
                {"title": {"contains": filters.search, "mode": "insensitive"}},
                {"model": {"contains": filters.search, "mode": "insensitive"}},
                {"rawMessage": {"contains": filters.search, "mode": "insensitive"}}
            ]
        
        # RAM filter (extract GB and compare)
        if filters.min_ram:
            # This is tricky with string fields - would need to filter in Python
            # For now, we'll skip this or you could add a separate ramGb integer field
            pass
        
        # Storage filter (similar issue)
        if filters.min_storage:
            pass
        
        return where
