import asyncio
import os
import re
from discord.ext import commands
import random
from dotenv import load_dotenv
import webserver_bot

load_dotenv()

TOKEN = os.getenv("TOKEN")

CHANNEL_TO_LISTEN_ID = int(os.getenv("CHANNEL_TO_LISTEN_ID"))

CLONE_CHANNEL_ID = int(os.getenv("CLONE_CHANNEL_ID"))

IGNORE_LIST = os.getenv("IGNORE_LIST")

IGNORE_LIST = IGNORE_LIST.split(",")

FORMATED_IGNORE_LIST = [int(i) for i in IGNORE_LIST]

bot = commands.Bot(command_prefix="~", self_bot=True)


@bot.event
async def on_ready():
    print(f"Bot online")


@bot.listen("on_message")
async def on_message(message):
    if message.author == bot.user:
        return

    if message.author.id in FORMATED_IGNORE_LIST:
        return

    clone_channel = bot.get_channel(CLONE_CHANNEL_ID)

    if message.channel.id == CHANNEL_TO_LISTEN_ID:

        images_to_send = []
        videos_to_send = []

        for attachment in message.attachments:
            if attachment.is_spoiler():
                continue

            file_url = attachment.url
            clean_url = file_url.split('?')[0]

            if any(clean_url.endswith(ext) for ext in [".jpeg", ".png", ".jpg", ".webp"]):
                image_file = await attachment.to_file()
                images_to_send.append(image_file)

            elif any(clean_url.endswith(ext) for ext in ['.mp4', '.mov', '.avi', '.webm', '.mkv']):
                videos_to_send.append(file_url)

        if len(images_to_send) > 0:
            await clone_channel.send(
                f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}",
                files=images_to_send)
            random_integer = random.randint(1, 10)
            await asyncio.sleep(random_integer)

        if len(videos_to_send) > 0:
            for video in videos_to_send:
                random_integer = random.randint(1, 10)
                await clone_channel.send(
                    f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}\n{video}")
                await asyncio.sleep(random_integer)

        if len(images_to_send) and len(videos_to_send) < 1:
            return

        if message.embeds:
            for embed in message.embeds:
                if embed.url:
                    await clone_channel.send(embed.url)
        else:
            url_pattern = r'https?://\S+'
            url_match = re.findall(url_pattern, message.content)
            if url_match:
                text_without_mentions = re.sub(r'@\S+', '', message.content)
                random_integer = random.randint(1, 10)
                await clone_channel.send(text_without_mentions)
                await asyncio.sleep(random_integer)


webserver_bot.keep_alive()

bot.run(TOKEN)