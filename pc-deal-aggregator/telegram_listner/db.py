from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["telegram_deals"]
raw_messages = db["raw_messages"]

def save_raw_message(message):
    raw_messages.insert_one(message)
