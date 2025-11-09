import os
import shutil

from dotenv import load_dotenv

load_dotenv()

level = os.getenv("LOG_LEVEL")

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