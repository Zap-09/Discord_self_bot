import asyncio
import os
import re
import random
import aiohttp
import discord
from discord.ext import commands
import dotenv

import webserver_bot
from imgcon.convet_func import convert_to_webp
from imgcon.utils import delete_folder

dotenv.load_dotenv()

TOKEN = os.getenv("TOKEN")

CHANNEL_TO_LISTEN_ID = int(os.getenv("CHANNEL_TO_LISTEN_ID"))

CLONE_CHANNEL_ID = int(os.getenv("CLONE_CHANNEL_ID"))

COMMAND_CHANNEL = int(os.getenv("COMMAND_CHANNEL"))

IGNORE_LIST = os.getenv("IGNORE_LIST", "")
FORMATED_IGNORE_LIST = [int(i) for i in IGNORE_LIST.split(",") if i]

MAX_FILE_SIZE = 10 * 1024 * 1024

bot = commands.Bot(command_prefix="/", self_bot=True)


def is_image_attachment(url):
    return url.lower().endswith((".jpeg", ".png", ".jpg", ".webp"))


def is_video_attachment(url):
    return url.lower().endswith((".mp4", ".mov", ".avi", ".webm", ".mkv"))


async def process_image_attachment(attachment):
    if attachment.size <= MAX_FILE_SIZE:
        return await attachment.to_file()

    os.makedirs("Temp", exist_ok=True)
    os.makedirs("Converted", exist_ok=True)

    async with aiohttp.ClientSession() as session:
        async with session.get(attachment.url) as resp:
            if resp.status != 200:
                return None
            temp_path = os.path.join("Temp", attachment.filename)
            with open(temp_path, "wb") as f:
                f.write(await resp.read())

    new_path, new_size = convert_to_webp(
        image_file=temp_path,
        output_path="Converted",
        lossless=True,
        compress_level=6
    )

    if new_size > MAX_FILE_SIZE:
        new_path, new_size = convert_to_webp(
            image_file=new_path,
            output_path="Converted",
            lossless=False,
            quality=80,
            compress_level=6
        )

    return discord.File(new_path)


async def process_forwarded_message(snapshot, clone_channel):
    forwarded = snapshot

    content = forwarded.content or ""
    attachments = forwarded.attachments or []

    to_send_files = []
    for att in attachments:
        if att.is_spoiler():
            continue
        if att.size <= MAX_FILE_SIZE:
            to_send_files.append(await att.to_file())

    if content:
        await clone_channel.send(content)

    if to_send_files:
        await clone_channel.send(files=to_send_files)


async def process_message(message, clone_channel):
    images = []
    videos = []
    sent_anything = False


    for attachment in message.attachments:
        if attachment.is_spoiler():
            continue

        clean_url = attachment.url.split("?")[0]
        if is_image_attachment(clean_url):
            file = await process_image_attachment(attachment)
            if file:
                images.append(file)

        elif is_video_attachment(clean_url):
            videos.append(attachment.url)


    for embed in message.embeds:
        if embed.image and embed.image.url:
            await clone_channel.send(embed.image.url)
            sent_anything = True
        if embed.thumbnail and embed.thumbnail.url:
            await clone_channel.send(embed.thumbnail.url)
            sent_anything = True


    if images:
        await clone_channel.send(
            f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}",
            files=images
        )
        sent_anything = True
        await asyncio.sleep(random.randint(1, 3))


    for video in videos:
        await clone_channel.send(
            f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}\n{video}"
        )
        sent_anything = True
        await asyncio.sleep(random.randint(1, 3))

    # URLs/text
    # Send each URL one at a time
    if not sent_anything:
        urls = re.findall(r"https?://\S+", message.content)

        for link in urls:
            await clone_channel.send(link)
            await asyncio.sleep(random.randint(1, 3))

    delete_folder("Temp")
    delete_folder("Converted")


async def send_as(message):
    clone_channel = bot.get_channel(CLONE_CHANNEL_ID)

    args = message.content[len("/send_as"):].strip()
    origin = args.strip()

    attachments = [att for att in message.attachments if not att.is_spoiler()]

    if not origin and not attachments:
        await message.channel.send("You must provide at least an origin or attachments.")
        return

    files = []
    for att in attachments:
        try:
            files.append(await att.to_file())
        except:
            continue

    if files:
        await clone_channel.send(origin,files=files)
        await asyncio.sleep(random.randint(1, 3))
    else:
        if origin:
            await clone_channel.send(origin)
            await asyncio.sleep(random.randint(1, 3))



async def send_embed(message):
    clone_channel = bot.get_channel(CLONE_CHANNEL_ID)

    urls = re.findall(r"https?://\S+", message.content)
    if not urls:
        await message.channel.send("No URLs found to send as embed.")
        return

    for link in urls:
        await clone_channel.send(link)
        await asyncio.sleep(random.randint(1, 3))



@bot.event
async def on_ready():
    print(f"Bot online as {bot.user}")



@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("/send_as") and message.channel.id == COMMAND_CHANNEL:
        await send_as(message)
        return

    if message.content.startswith("/send_embed") and message.channel.id == COMMAND_CHANNEL:
        await send_embed(message)
        return

    if message.author.id in FORMATED_IGNORE_LIST:
        return

    clone_channel = bot.get_channel(CLONE_CHANNEL_ID)


    snapshots = getattr(message, "message_snapshots", None)
    if snapshots:
        for snap in snapshots:
            await process_forwarded_message(snap, clone_channel)
        return


    if message.channel.id == CHANNEL_TO_LISTEN_ID:
        await process_message(message, clone_channel)


webserver_bot.keep_alive()

bot.run(TOKEN)