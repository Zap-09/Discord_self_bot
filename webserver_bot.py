import os

from flask import Flask, render_template
from threading import Thread
import requests
import logging

app = Flask("")

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

def ping(url):
    try:
        response = requests.get(url,timeout=120)
        if response.status_code != 200:
            print(f"Error:external server status code {response.status_code}")
    except:
        pass

def ping_website(url):
    if url is None:
        return
    t = Thread(target=ping, args=(url,))
    t.start()

@app.route("/")
def home():
    ping_website(os.getenv("KEEP_ALIVE_URL"))
    ping_website(os.getenv("KEEP_ALIVE_OTHER_BOT",None))
    return render_template("index.html")


def run():
    app.run(host="0.0.0.0",port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()