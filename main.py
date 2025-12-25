import asyncio
import os
import re
import discord
from discord.ext import commands
import random
from dotenv import load_dotenv
import webserver_bot
import aiohttp

from imgcon.convet_func import convert_to_webp
from imgcon.utils import delete_folder, send_messages

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
    os.makedirs("temp",exist_ok=True)
    os.makedirs("Converted",exist_ok=True)
    if message.author == bot.user:
        return

    if message.author.id in FORMATED_IGNORE_LIST:
        return

    clone_channel = bot.get_channel(CLONE_CHANNEL_ID)

    if message.channel.id == CHANNEL_TO_LISTEN_ID:

        images_to_send = []
        videos_to_send = []
        max_file_size = 10 * 1024 * 1024

        for attachment in message.attachments:
            if attachment.is_spoiler():
                continue

            file_url = attachment.url
            clean_url = file_url.split("?")[0]

            if any(clean_url.endswith(ext) for ext in [".jpeg", ".png", ".jpg", ".webp"]):
                if attachment.size > max_file_size:
                    os.makedirs("Temp",exist_ok=True)
                    async with aiohttp.ClientSession() as session:
                        async with session.get(file_url) as response:
                            if response.status == 200:
                                with open(os.path.join("Temp",attachment.filename),"wb") as f:
                                    f.write(await response.read())
                                    new_file_name,new_file_size = convert_to_webp(
                                        image_file = os.path.join("Temp",attachment.filename),
                                        output_path= os.path.join("Converted"),
                                        lossless=True,
                                        compress_level=6
                                    )
                                    if new_file_size > max_file_size:
                                       new_file_name,new_file_size = convert_to_webp(
                                            image_file=new_file_name,
                                            output_path=os.path.join("Converted"),
                                            lossless=False,
                                            quality= 80,
                                            compress_level=6
                                        )
                                    try:
                                        discord_file = discord.File(new_file_name)
                                        images_to_send.append(discord_file)
                                    except Exception as e:
                                        send_messages(f"Error at line 83 : {e}")
                            else:
                                print(f"Failed to download the file: {response.status}")
                else:
                    try:
                        image_file = await attachment.to_file()
                        images_to_send.append(image_file)
                    except Exception as e:
                        send_messages(f"Error at line 90 : {e}")

            elif any(clean_url.endswith(ext) for ext in [".mp4", ".mov", ".avi", ".webm", ".mkv"]):
                videos_to_send.append(file_url)

        if len(images_to_send) > 0:
            try:
                await clone_channel.send(
                    f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}",
                    files=images_to_send)
            except Exception as e:
                send_messages(f"Error at line 101 : {e}")
            random_integer = random.randint(1, 3)
            await asyncio.sleep(random_integer)

        if len(videos_to_send) > 0:
            for video in videos_to_send:
                random_integer = random.randint(1, 3)
                await clone_channel.send(
                    f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}\n{video}")
                await asyncio.sleep(random_integer)
        delete_folder("Temp")
        delete_folder("Converted")

        if len(images_to_send) and len(videos_to_send) < 1:
            return

        if message.embeds:
            for embed in message.embeds:
                if embed.url:
                    embed_url = embed.url
                    clean_embed_url = embed_url.split("?")[0]
                    if any(clean_embed_url.endswith(ext) for ext in [".gif"]):
                        pass
                    else:
                        await clone_channel.send(embed.url)
        else:
            url_pattern = r"https?://\S+"
            url_match = re.findall(url_pattern, message.content)
            if url_match:
                text_without_mentions = re.sub(r"@\S+", "", message.content)
                random_integer = random.randint(1, 3)
                await clone_channel.send(text_without_mentions)
                await asyncio.sleep(random_integer)


webserver_bot.keep_alive()

bot.run(TOKEN)