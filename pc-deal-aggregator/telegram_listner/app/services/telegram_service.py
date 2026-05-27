"""
Telegram listener service using Telethon
"""
import os
import sys
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from telethon import TelegramClient, events
from app.core.config import settings
from app.core.phone import normalize_phone
from app.core.database import prisma
from app.parsers.hybrid_parser import HybridParser
from app.services.deal_service import DealService

DEAL_KEYWORDS = re.compile(
    r"laptop|notebook|macbook|core\s*i[3579]|ryzen|"
    r"\d+\s*gb\s*ram|\d+\s*(?:tb|gb)\s*ssd|"
    r"price|birr|hp\s|dell\s|lenovo|asus|acer|pavilion|thinkpad",
    re.IGNORECASE,
)


class TelegramService:
    """Service for listening to Telegram channels and processing messages"""

    def __init__(self):
        self.client = TelegramClient(
            settings.TELEGRAM_SESSION_NAME,
            settings.TELEGRAM_API_ID,
            settings.TELEGRAM_API_HASH,
        )
        self.parser = HybridParser()
        self.is_running = False

    def _session_path(self) -> Path:
        return Path(f"{settings.TELEGRAM_SESSION_NAME}.session")

    async def _ensure_connected(self) -> None:
        if self.client.is_connected():
            return
        if not self._session_path().exists() and not sys.stdin.isatty():
            raise RuntimeError(
                "Telegram is not logged in. Run: python telegram_login.py"
            )
        phone = settings.TELEGRAM_PHONE or os.getenv("TELEGRAM_PHONE")
        if phone:
            await self.client.start(phone=normalize_phone(phone))
        else:
            await self.client.start()

    async def connect(self) -> None:
        """Connect only (no live listener) — use for historical scraping."""
        await self._ensure_connected()
        print("[OK] Telegram client connected")

    async def start(self):
        """Start the Telegram client and register live message handlers."""
        if self.is_running:
            print("[WARN] Telegram service already running")
            return

        await self._ensure_connected()
        print("[OK] Telegram client started")
        print(f"[*] Watching channels: {', '.join(settings.watched_channels)}")

        @self.client.on(events.NewMessage(chats=settings.watched_channels))
        async def handle_new_message(event):
            await self._process_message(event)

        self.is_running = True

    async def stop(self):
        """Stop the Telegram client"""
        if self.client.is_connected():
            await self.client.disconnect()
        self.is_running = False
        print("[OK] Telegram client stopped")

    async def run_until_disconnected(self):
        """Keep the client running"""
        await self.client.run_until_disconnected()

    def _looks_like_deal(self, text: str, parsed: dict) -> bool:
        if parsed.get("price"):
            return True
        if parsed.get("processor") or parsed.get("ram") or parsed.get("storage"):
            return True
        return bool(DEAL_KEYWORDS.search(text))

    async def _process_message(self, event, download_images: bool = True):
        """Process a new Telegram message"""
        try:
            message_text = event.message.message or ""

            if not message_text.strip():
                print("[SKIP] Empty message")
                return

            print(f"\n[MSG] New message from {event.chat.username or event.chat_id}")
            print(f"   Preview: {message_text[:100]}...")

            media_path = None
            if download_images and event.message.media:
                media_folder = "downloaded_images"
                os.makedirs(media_folder, exist_ok=True)
                media_path = f"{media_folder}/{event.id}.jpg"
                await event.download_media(file=media_path)
                print(f"   [IMG] Downloaded image: {media_path}")

            parsed_data = self.parser.parse(message_text)
            parsed_data["image_path"] = media_path
            parsed_data["channel_id"] = str(event.chat_id)
            parsed_data["message_id"] = str(event.id)
            if event.message.date:
                parsed_data["posted_at"] = event.message.date

            if event.chat.username:
                parsed_data["telegram_url"] = (
                    f"https://t.me/{event.chat.username}/{event.id}"
                )

            deal_service = DealService(prisma)
            deal = await deal_service.create_deal(parsed_data)

            print(f"   [OK] Saved deal: {deal.id}")
            print(f"   Title: {deal.title}")
            print(f"   Price: {deal.price} {deal.currency}")

        except ValueError as e:
            if str(e) == "duplicate":
                print("   [SKIP] Already in database")
            else:
                raise
        except Exception as e:
            print(f"   [FAIL] Error processing message: {e}")
            import traceback
            traceback.print_exc()

    async def scrape_history(
        self,
        channel: str,
        days_back: int | None = None,
        limit: int | None = None,
        download_images: bool | None = None,
        require_deal_signal: bool | None = None,
    ):
        """
        Scrape historical messages from a channel (newest to oldest).

        Stops when messages are older than days_back.
        """
        days_back = days_back if days_back is not None else settings.SCRAPE_DAYS_BACK
        limit = limit if limit is not None else settings.SCRAPE_LIMIT_PER_CHANNEL
        download_images = (
            download_images
            if download_images is not None
            else settings.SCRAPE_DOWNLOAD_IMAGES
        )
        require_deal_signal = (
            require_deal_signal
            if require_deal_signal is not None
            else settings.SCRAPE_REQUIRE_DEAL_SIGNAL
        )

        cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)

        print(f"\n[*] Scraping history from {channel}")
        print(f"   Window: last {days_back} days (since {cutoff.date()})")
        print(f"   Max messages: {limit}")
        print(f"   Images: {'on' if download_images else 'off'}")

        await self._ensure_connected()

        deal_service = DealService(prisma)
        processed = 0
        saved = 0
        skipped_dup = 0
        skipped_filter = 0
        errors = 0

        async for message in self.client.iter_messages(channel, limit=limit):
            processed += 1

            if message.date and message.date.replace(tzinfo=timezone.utc) < cutoff:
                print(f"   Reached cutoff date ({cutoff.date()}), stopping.")
                break

            if not message.message or not message.message.strip():
                continue

            text = message.message
            channel_id = str(message.chat_id)
            message_id = str(message.id)

            try:
                if await deal_service.deal_exists(channel_id, message_id):
                    skipped_dup += 1
                    continue

                parsed_data = self.parser.parse(text)

                if require_deal_signal and not self._looks_like_deal(text, parsed_data):
                    skipped_filter += 1
                    continue

                parsed_data["image_path"] = None
                if download_images and message.media:
                    media_folder = "downloaded_images"
                    os.makedirs(media_folder, exist_ok=True)
                    media_path = f"{media_folder}/{message.id}.jpg"
                    await message.download_media(file=media_path)
                    parsed_data["image_path"] = media_path

                parsed_data["channel_id"] = channel_id
                parsed_data["message_id"] = message_id
                if message.date:
                    parsed_data["posted_at"] = message.date

                chat = await message.get_chat()
                if getattr(chat, "username", None):
                    parsed_data["telegram_url"] = (
                        f"https://t.me/{chat.username}/{message.id}"
                    )

                await deal_service.create_deal(parsed_data)
                saved += 1

                if saved % 25 == 0:
                    print(
                        f"   Progress: {processed} scanned, {saved} saved, "
                        f"{skipped_dup} dup, {skipped_filter} filtered"
                    )

            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"   [WARN] Message {message_id}: {e}")

        print(f"\n[OK] Finished {channel}")
        print(f"   Scanned: {processed}")
        print(f"   Saved: {saved}")
        print(f"   Duplicates skipped: {skipped_dup}")
        print(f"   Filtered (non-deal): {skipped_filter}")
        print(f"   Errors: {errors}")

        return {
            "processed": processed,
            "saved": saved,
            "skipped_dup": skipped_dup,
            "skipped_filter": skipped_filter,
            "errors": errors,
        }


telegram_service = TelegramService()
