from client import client
from telethon import events
from parser import parse_message 

# Rename WATCHED_CHANNELS to CHANNEL_IDS
CHANNEL_IDS = ["@pcagregator", "https://t.me/pcagregator"]

@client.on(events.NewMessage(chats=CHANNEL_IDS))
async def handle_new_message(event):
    message_text = event.message.message
    parsed_data = parse_message(message_text)

    # Print data to terminal BEFORE saving
    print("==== New Deal Received ====")
    print(f"Original Message:\n{message_text}\n")
    print("Parsed Result:")
    print(parsed_data)
