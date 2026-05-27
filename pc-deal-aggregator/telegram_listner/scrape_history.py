"""
Backfill historical PC deals from Telegram channels into PostgreSQL.

Usage:
    python scrape_history.py           # interactive confirm
    python scrape_history.py --yes     # skip confirm
    python scrape_history.py --channel @samcomptech --days 180
"""
import argparse
import asyncio
import sys

from app.core.config import settings
from app.core.database import connect_db, disconnect_db
from app.services.telegram_service import telegram_service


async def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape historical Telegram PC deals")
    parser.add_argument(
        "--yes", "-y", action="store_true", help="Skip confirmation prompt"
    )
    parser.add_argument(
        "--channel",
        action="append",
        metavar="CHANNEL",
        help=(
            "Scrape only this channel (repeatable). "
            'On PowerShell quote it: --channel "@samcomptech"'
        ),
    )
    parser.add_argument(
        "--days",
        type=int,
        default=None,
        help=f"Days of history (default: {settings.SCRAPE_DAYS_BACK})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=f"Max messages per channel (default: {settings.SCRAPE_LIMIT_PER_CHANNEL})",
    )
    args = parser.parse_args()

    channels = args.channel or settings.scrape_channels
    days_back = args.days if args.days is not None else settings.SCRAPE_DAYS_BACK
    limit = args.limit if args.limit is not None else settings.SCRAPE_LIMIT_PER_CHANNEL

    print("""
    ===========================================================
           PC Deal Aggregator - Historical Backfill
    ===========================================================
    """)
    print("[*] Live listener is NOT used — run scrape only.")
    print(f"    Channels: {', '.join(channels)}")
    print(f"    History:  last {days_back} days (~6 months)")
    print(f"    Limit:    {limit} messages per channel")
    print(f"    Images:   {'on' if settings.SCRAPE_DOWNLOAD_IMAGES else 'off'}")
    print()

    if not args.yes:
        answer = input("Start scraping? (y/n): ").strip().lower()
        if answer != "y":
            print("Cancelled.")
            return

    totals = {"processed": 0, "saved": 0, "skipped_dup": 0, "skipped_filter": 0, "errors": 0}

    try:
        await connect_db()
        await telegram_service.connect()

        for channel in channels:
            result = await telegram_service.scrape_history(
                channel=channel,
                days_back=days_back,
                limit=limit,
            )
            for key in totals:
                totals[key] += result.get(key, 0)

        print("\n" + "=" * 60)
        print("[OK] All channels complete")
        print("=" * 60)
        print(f"Total scanned:  {totals['processed']}")
        print(f"Total saved:    {totals['saved']}")
        print(f"Duplicates:     {totals['skipped_dup']}")
        print(f"Filtered out:   {totals['skipped_filter']}")
        print(f"Errors:         {totals['errors']}")
        if totals["processed"]:
            rate = totals["saved"] / totals["processed"] * 100
            print(f"Save rate:      {rate:.1f}%")

    except KeyboardInterrupt:
        print("\n[*] Interrupted by user")
    except Exception as e:
        print(f"\n[FAIL] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await telegram_service.stop()
        await disconnect_db()


if __name__ == "__main__":
    asyncio.run(main())
