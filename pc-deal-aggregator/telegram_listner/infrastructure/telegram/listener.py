from telethon import events
from infrastructure.telegram.client import client
from app.use_cases.parse_deal_use_case import ParseDealUseCase
from infrastructure.database.deal_repository import DealRepository
import os

WATCHED_CHANNELS = os.getenv("WATCHED_CHANNELS", "@pcagregator").split(",")

parser_use_case = ParseDealUseCase()

@client.on(events.NewMessage(chats=WATCHED_CHANNELS))
async def handle_new_message(event):
    message_text = event.message.message or ""  # make sure this is always a string

    # Debug print
    print(f"Received message text:\n{message_text}")

    media_path = None
    if event.message.media:
        media_folder = "downloaded_images"
        os.makedirs(media_folder, exist_ok=True)
        media_path = f"{media_folder}/{event.id}.jpg"
        await event.download_media(file=media_path)

    parsed_data = parser_use_case.parse(message_text)

    # Always keep the raw message as-is
    parsed_data["raw_message"] = message_text
    parsed_data["image_path"] = media_path

    inserted_id = DealRepository.insert(parsed_data)

    print(f"Inserted deal {inserted_id} with data: {parsed_data}")

