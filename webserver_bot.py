import os

from flask import Flask, render_template
from threading import Thread
import requests
app = Flask("__name__")

@app.route("/")
def home():
    try:
        response = requests.get(os.getenv("KEEP_ALIVE_URL"),timeout=120)
        if response.status_code != 200:
            print(f"Error:external server status code {response.status_code}")
    except:
        pass
    return render_template("index.html")


def run():
    app.run(host="0.0.0.0",port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()