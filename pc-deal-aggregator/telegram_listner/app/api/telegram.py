"""
Telegram control endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from app.services.telegram_service import telegram_service

router = APIRouter(prefix="/telegram", tags=["Telegram"])


class ScrapeRequest(BaseModel):
    """Request model for scraping history"""
    channel: str
    limit: int = 100
    days_back: Optional[int] = None  # How many days back to scrape


@router.post("/start")
async def start_telegram_listener(background_tasks: BackgroundTasks):
    """
    Start the Telegram listener service
    """
    if telegram_service.is_running:
        return {
            "message": "Telegram service is already running",
            "status": "running"
        }
    
    # Start in background
    background_tasks.add_task(telegram_service.start)
    background_tasks.add_task(telegram_service.run_until_disconnected)
    
    return {
        "message": "Telegram service starting...",
        "status": "starting"
    }


@router.post("/stop")
async def stop_telegram_listener():
    """
    Stop the Telegram listener service
    """
    if not telegram_service.is_running:
        return {
            "message": "Telegram service is not running",
            "status": "stopped"
        }
    
    await telegram_service.stop()
    
    return {
        "message": "Telegram service stopped",
        "status": "stopped"
    }


@router.get("/status")
async def get_telegram_status():
    """
    Get Telegram service status
    """
    return {
        "status": "running" if telegram_service.is_running else "stopped",
        "is_connected": telegram_service.client.is_connected() if telegram_service.is_running else False
    }


@router.post("/scrape")
async def scrape_channel_history(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Scrape historical messages from a channel
    
    This runs in the background and returns immediately.
    Check the logs or database for progress.
    """
    # Calculate offset date if days_back is provided
    offset_date = None
    if request.days_back:
        offset_date = datetime.now() - timedelta(days=request.days_back)
    
    # Run scraping in background
    background_tasks.add_task(
        telegram_service.scrape_history,
        channel=request.channel,
        limit=request.limit,
        offset_date=offset_date
    )
    
    return {
        "message": f"Started scraping {request.channel}",
        "channel": request.channel,
        "limit": request.limit,
        "days_back": request.days_back,
        "status": "scraping"
    }
