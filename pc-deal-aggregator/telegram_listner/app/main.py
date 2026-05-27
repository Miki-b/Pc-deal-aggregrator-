"""
FastAPI application for PC Deal Aggregator
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.database import connect_db, disconnect_db
from app.api import health_router, deals_router, telegram_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    print(f"\n🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    await connect_db()
    
    yield
    
    # Shutdown
    print("\n👋 Shutting down...")
    await disconnect_db()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API for aggregating and analyzing PC deals from Telegram channels",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for images
if os.path.exists("downloaded_images"):
    app.mount("/images", StaticFiles(directory="downloaded_images"), name="images")

# Include routers
app.include_router(health_router)
app.include_router(deals_router, prefix="/api/v1")
app.include_router(telegram_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
