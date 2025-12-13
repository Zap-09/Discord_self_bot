import os
import shutil
import requests

from dotenv import load_dotenv

load_dotenv()

level = os.getenv("LOG_LEVEL")

NOTIFY_TOKEN = os.getenv("NOTIFIER_TOKEN")

NOTIFY_CHANNEL_ID = os.getenv("NOTIFY_CHANNEL_ID")

if not level:
    level = "info"
else:
    level.lower()


def log(msg,t="info"):
    if level == "none":
        return

    if level == "--info":
        if t == "info":
            print(msg)
    elif level == "--warn":
        if t == "warn":
            print(msg)
    elif level == "--error":
        if t == "error":
            print(msg)

    log_type = []

    if level == "info":
        log_type = ["info","warn","error"]
    elif level == "warn":
        log_type = ["warn", "error"]
    elif level == "error":
        log_type = ["error"]
    if t in log_type:
        print(msg)



def delete_folder(folder_path):
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
        except Exception as e:
            log(f"Error while deleting the folder: {e}",t="error")
    else:
        log(f"The folder '{folder_path}' does not exist.",t="error")


def send_messages(message:str):
    url = f"https://discord.com/api/v10/channels/{NOTIFY_CHANNEL_ID}/messages"
    headers = {
        "Authorization": f"Bot {NOTIFY_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "content": f"<Discord_self_bot> {message}"
    }
    response = requests.post(url,headers=headers,json=payload)
    if not response.status_code in (200,201):
        print(f"Failed to send the message: {response.status_code} - {response.text}")
