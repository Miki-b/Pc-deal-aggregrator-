"""
Health check endpoints
"""
from fastapi import APIRouter, Depends
from app.core.database import prisma, get_db
from app.services.telegram_service import telegram_service
from app.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@router.get("/health/db")
async def database_health():
    """Check database connection"""
    try:
        from app.core.database import connect_db

        await connect_db()
        count = await prisma.deal.count()
        return {
            "status": "healthy",
            "database": "connected",
            "deals_count": count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


@router.get("/health/telegram")
async def telegram_health():
    """Check Telegram service status"""
    return {
        "status": "healthy" if telegram_service.is_running else "stopped",
        "telegram": "connected" if telegram_service.is_running else "disconnected",
        "watched_channels": settings.watched_channels
    }
