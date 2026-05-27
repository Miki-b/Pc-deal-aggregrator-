"""
Standalone script to run the Telegram listener
This is an alternative to starting it via the API
"""
import asyncio
import sys
from pathlib import Path

from app.core.config import settings
from app.core.database import connect_db, disconnect_db
from app.services.telegram_service import telegram_service


async def main():
    """Main function to run the listener"""
    print("""
    ===========================================================
              PC Deal Aggregator - Telegram Listener
    ===========================================================
    """)
    
    print("\n[!] Live listener mode.")
    print("    For 6-month backfill use:  python scrape_history.py --yes")
    print("    (see SCRAPE_GUIDE.md)\n")

    session_file = Path(f"{settings.TELEGRAM_SESSION_NAME}.session")
    if not session_file.exists():
        print("[!] No Telegram session found.")
        print("    First-time setup: run  python telegram_login.py\n")

    try:
        print("\n[*] Connecting to database...")
        await connect_db()
        
        print("[*] Starting Telegram listener...")
        await telegram_service.start()
        
        print("\n[OK] Listener is running!")
        print("[*] Watching for new messages...")
        print("\nPress Ctrl+C to stop\n")
        
        # Run until disconnected
        await telegram_service.run_until_disconnected()
        
    except KeyboardInterrupt:
        print("\n\n[*] Stopping listener...")
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Cleanup
        await telegram_service.stop()
        await disconnect_db()
        print("Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
