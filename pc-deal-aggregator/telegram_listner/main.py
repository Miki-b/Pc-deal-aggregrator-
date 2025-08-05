from infrastructure.telegram.client import client
import infrastructure.telegram.listener  # to register handlers

if __name__ == "__main__":
    client.start()
    print("Telegram listener started...")
    client.run_until_disconnected()
