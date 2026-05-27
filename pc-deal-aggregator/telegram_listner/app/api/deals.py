"""
Deal API endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from app.core.database import prisma
from app.services.deal_service import DealService
from app.models.deal import (
    DealResponse,
    DealFilter,
    DealStats,
    PaginatedDeals
)
import math

router = APIRouter(prefix="/deals", tags=["Deals"])


@router.get("", response_model=PaginatedDeals)
async def get_deals(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("createdAt", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    # Filters
    min_price: Optional[int] = Query(None, description="Minimum price"),
    max_price: Optional[int] = Query(None, description="Maximum price"),
    categories: Optional[str] = Query(None, description="Comma-separated categories"),
    processor: Optional[str] = Query(None, description="Processor filter"),
    graphics_card: Optional[str] = Query(None, description="Graphics card filter"),
    condition: Optional[str] = Query(None, description="Condition filter"),
    min_score: Optional[int] = Query(None, description="Minimum general score"),
    search: Optional[str] = Query(None, description="Search in title/model/message"),
):
    """
    Get paginated list of deals with optional filtering
    """
    # Build filters
    filters = DealFilter(
        minPrice=min_price,
        maxPrice=max_price,
        categories=categories.split(",") if categories else None,
        processor=processor,
        graphicsCard=graphics_card,
        condition=condition,
        minScore=min_score,
        search=search
    )
    
    # Calculate skip
    skip = (page - 1) * page_size
    
    # Get deals
    deal_service = DealService(prisma)
    deals, total = await deal_service.get_deals(
        skip=skip,
        limit=page_size,
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Calculate total pages
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    return PaginatedDeals(
        deals=[DealResponse.model_validate(deal) for deal in deals],
        total=total,
        page=page,
        pageSize=page_size,
        totalPages=total_pages
    )


@router.get("/stats", response_model=DealStats)
async def get_deal_stats(
    # Filters
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    categories: Optional[str] = Query(None),
    processor: Optional[str] = Query(None),
    graphics_card: Optional[str] = Query(None),
    condition: Optional[str] = Query(None),
    min_score: Optional[int] = Query(None),
):
    """
    Get statistics about deals
    """
    filters = DealFilter(
        minPrice=min_price,
        maxPrice=max_price,
        categories=categories.split(",") if categories else None,
        processor=processor,
        graphicsCard=graphics_card,
        condition=condition,
        minScore=min_score
    )
    
    deal_service = DealService(prisma)
    stats = await deal_service.get_deal_stats(filters)
    
    return stats


@router.get("/{deal_id}", response_model=DealResponse)
async def get_deal(deal_id: str):
    """
    Get a specific deal by ID
    """
    deal_service = DealService(prisma)
    deal = await deal_service.get_deal_by_id(deal_id)
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    return DealResponse.model_validate(deal)


@router.delete("/{deal_id}")
async def delete_deal(deal_id: str):
    """
    Delete a deal by ID
    """
    deal_service = DealService(prisma)
    success = await deal_service.delete_deal(deal_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    return {"message": "Deal deleted successfully", "id": deal_id}


@router.get("/categories/list")
async def get_categories():
    """
    Get list of all unique categories
    """
    # Get all deals and extract unique categories
    deals = await prisma.deal.find_many(select={"categories": True})
    
    categories = set()
    for deal in deals:
        categories.update(deal.categories)
    
    return {"categories": sorted(list(categories))}


@router.get("/brands/list")
async def get_brands():
    """
    Get list of all unique brands (extracted from titles)
    """
    deals = await prisma.deal.find_many(select={"title": True})
    
    brands = set()
    for deal in deals:
        if deal.title:
            # Extract first word as brand
            brand = deal.title.split()[0]
            brands.add(brand)
    
    return {"brands": sorted(list(brands))}
