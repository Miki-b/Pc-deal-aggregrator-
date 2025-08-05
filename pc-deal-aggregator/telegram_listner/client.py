from telethon import TelegramClient
import os
from dotenv import load_dotenv

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

client = TelegramClient("session_name", api_id, api_hash)
