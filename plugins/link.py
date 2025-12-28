import re, asyncio, time, shutil, psutil, os, sys
from pyrogram import Client, filters, enums
from pyrogram.types import *
from info import ADMINS
from urllib.parse import quote_plus

BOT_USERNAME = None  # cache bot username

@Client.on_message(filters.command("link") & filters.user(ADMINS))
async def generate_link(client, message):
    global BOT_USERNAME

    # Get bot username once
    if BOT_USERNAME is None:
        me = await client.get_me()
        BOT_USERNAME = me.username

    # Validate argument
    if len(message.command) < 2:
        return await message.reply(
            "❗ **Please provide movie name**\n\n"
            "**Example:**\n`/link game of thrones`",
            parse_mode=enums.ParseMode.MARKDOWN
        )

    # Create URL-safe movie slug
    movie_name = quote_plus(" ".join(message.command[1:]).lower())

    # 🔥 PLAIN TEXT deep-link (NO base64)
    link = f"https://t.me/{BOT_USERNAME}?start=getfile-{movie_name}"

    await message.reply(
        text=f"✅ **Your link is ready:**\n\n{link}",
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(
                    "🔗 Share Link",
                    url=f"https://telegram.me/share/url?url={link}"
                )
            ]]
        ),
        disable_web_page_preview=True
    )
