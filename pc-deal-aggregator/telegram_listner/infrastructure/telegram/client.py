import os
from telethon import TelegramClient
from dotenv import load_dotenv
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "session")

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
