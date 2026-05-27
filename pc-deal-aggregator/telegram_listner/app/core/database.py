"""
Prisma database client initialization and management
"""
import asyncio
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from prisma import Prisma

# Global Prisma client instance
prisma = Prisma()

CONNECT_RETRIES = int(os.getenv("DB_CONNECT_RETRIES", "3"))
CONNECT_RETRY_DELAY_SEC = float(os.getenv("DB_CONNECT_RETRY_DELAY_SEC", "5"))


async def connect_db() -> None:
    """Connect to the database with retries (helps Neon cold starts)."""
    if prisma.is_connected():
        return

    last_error: Exception | None = None
    for attempt in range(1, CONNECT_RETRIES + 1):
        try:
            await prisma.connect()
            print("[OK] Database connected")
            return
        except Exception as exc:
            last_error = exc
            if attempt < CONNECT_RETRIES:
                print(
                    f"[WARN] Database connect attempt {attempt}/{CONNECT_RETRIES} failed, "
                    f"retrying in {CONNECT_RETRY_DELAY_SEC}s..."
                )
                await asyncio.sleep(CONNECT_RETRY_DELAY_SEC)

    raise RuntimeError(
        "Could not connect to PostgreSQL. "
        "Check DATABASE_URL in .env, that Neon/Postgres is active, and "
        "disable VPN if you see SSL or 'network name no longer available' errors."
    ) from last_error


async def disconnect_db() -> None:
    """Disconnect from the database"""
    if prisma.is_connected():
        await prisma.disconnect()
        print("[OK] Database disconnected")


@asynccontextmanager
async def get_db() -> AsyncGenerator[Prisma, None]:
    """
    Dependency for getting database session in FastAPI routes

    Usage:
        @app.get("/deals")
        async def get_deals(db: Prisma = Depends(get_db)):
            deals = await db.deal.find_many()
            return deals
    """
    try:
        if not prisma.is_connected():
            await connect_db()
        yield prisma
    finally:
        pass  # Keep connection alive for reuse
