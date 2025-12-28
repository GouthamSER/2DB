import re, asyncio, time
from pyrogram import Client, filters, enums
from pyrogram.types import *
from info import ADMINS
from urllib.parse import quote_plus

@Client.on_message(filters.command("link") & filters.user(ADMINS))
async def generate_link(client, message):
    """
    Generates a shareable Telegram deep link, replacing spaces with underscores
    in the payload for cleaner deep links.
    """
    try:
        # 1. Validate argument
        if len(message.command) < 2:
            return await message.reply(
                text=(
                    "❗ **Please provide movie name**\n\n"
                    "**Example:**\n`/link game of thrones`"
                ),
                parse_mode=enums.ParseMode.MARKDOWN
            )

        # Get bot username
        bot_username = client.me.username

        # 2. Create URL-safe movie slug with underscores
        # a. Join command parts and convert to lowercase
        movie_query = " ".join(message.command[1:]).lower()
        
        # b. Replace spaces with underscores
        movie_slug_with_underscores = movie_query.replace(" ", "_")
        
        # c. Apply quote_plus just to handle any *other* special characters 
        #    (though underscores and hyphens are usually fine).
        #    Note: For this specific use case (only replacing spaces), 
        #    quote_plus might be redundant after the replacement, but it's safe.
        final_movie_slug = quote_plus(movie_slug_with_underscores)

        # 🔥 PLAIN TEXT deep-link (using the underscore slug)
        link = f"https://t.me/{bot_username}?start=getfile-{final_movie_slug}"

        # 3. Send the response
        await message.reply(
            text=f"✅ **Your link is ready:**\n\n`{link}`",
            reply_markup=InlineKeyboardMarkup(
                [[
                    InlineKeyboardButton(
                        text="🔗 Share Link",
                        url=f"https://telegram.me/share/url?url={link}"
                    )
                ]]
            ),
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.MARKDOWN
        )

    except Exception as e:
        # Basic error handling
        print(f"Error in generate_link: {e}")
        await message.reply_text("An unexpected error occurred while generating the link.")
