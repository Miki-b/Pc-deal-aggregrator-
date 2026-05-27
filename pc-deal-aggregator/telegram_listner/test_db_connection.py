"""
Test database connection
"""
import asyncio
import os
import sys

from dotenv import load_dotenv

load_dotenv()


def _mask_url(url: str | None) -> str:
    if not url:
        return "(not set)"
    try:
        scheme, rest = url.split("://", 1)
        creds, hostpart = rest.split("@", 1)
        user = creds.split(":")[0]
        return f"{scheme}://{user}:***@{hostpart[:60]}..."
    except ValueError:
        return url[:60] + "..."


async def test_connection() -> bool:
    """Test if we can connect to the database"""
    database_url = os.getenv("DATABASE_URL")
    direct_url = os.getenv("DIRECT_DATABASE_URL")

    print("Testing database connection...")
    print(f"DATABASE_URL:        {_mask_url(database_url)}")
    print(f"DIRECT_DATABASE_URL: {_mask_url(direct_url)}")

    if not database_url:
        print("[FAIL] DATABASE_URL is not set in .env")
        return False

    if direct_url and "-pooler" in direct_url:
        print(
            "[WARN] DIRECT_DATABASE_URL should use the non-pooler Neon host "
            "(remove '-pooler' from the hostname)."
        )

    try:
        from prisma import Prisma

        db = Prisma()
        await db.connect()
        print("[OK] Successfully connected to database!")

        count = await db.deal.count()
        print(f"[OK] Database is working! Current deals count: {count}")

        await db.disconnect()
        return True

    except Exception as e:
        print(f"[FAIL] Connection failed: {e}")
        print("\nPossible solutions:")
        print("1. Open Neon dashboard — confirm project is Active (not suspended)")
        print("2. Copy fresh connection strings (pooled + direct) into .env")
        print("3. Run: prisma generate && prisma db push")
        print("4. Disable VPN (ProtonVPN etc.) — often breaks PostgreSQL SSL")
        return False


if __name__ == "__main__":
    ok = asyncio.run(test_connection())
    sys.exit(0 if ok else 1)
