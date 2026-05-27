from .health import router as health_router
from .deals import router as deals_router
from .telegram import router as telegram_router

__all__ = ["health_router", "deals_router", "telegram_router"]
