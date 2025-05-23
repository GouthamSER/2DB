import logging
import logging.config

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)

from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from database.ia_filterdb import Media, Media2, choose_mediaDB, db as clientDB
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR, LOG_CHANNEL, SECONDDB_URI, DATABASE_URI
from utils import temp
from typing import Union, Optional, AsyncGenerator
from pyrogram import types

# for prevent stoping the bot after 1 week
logging.getLogger("asyncio").setLevel(logging.CRITICAL -1)

# peer id invaild fixxx
from pyrogram import utils as pyroutils
pyroutils.MIN_CHAT_ID = -999999999999
pyroutils.MIN_CHANNEL_ID = -100999999999999

from plugins.webcode import bot_run
from os import environ
from aiohttp import web as webserver

from sample_info import tempDict

PORT_CODE = environ.get("PORT", "8080")

class Bot(Client):

    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        await super().start()
        await Media.ensure_indexes()
        await Media2.ensure_indexes()
        #choose the right db by checking the free space
        stats = await clientDB.command('dbStats')
        #calculating the free db space from bytes to MB
        free_dbSize = round(512-((stats['dataSize']/(1024*1024))+(stats['indexSize']/(1024*1024))), 2)
        if SECONDDB_URI and free_dbSize<320: #if the primary db have less than 350 MB left, use second DB.
            tempDict["indexDB"] = SECONDDB_URI
            logging.info(f"Since Primary DB have only {free_dbSize} MB left, Secondary DB will be used to store datas.")
        elif SECONDDB_URI is None:
            logging.error("Missing second DB URI !\n\nAdd SECONDDB_URI now !\n\nExiting...")
            exit()
        else:
            logging.info(f"Since primary DB have enough space ({free_dbSize}MB) left, It will be used for storing datas.")
        await choose_mediaDB()
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username
        logging.info(f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
       # logging.info(LOG_STR)
        await self.send_message(chat_id=LOG_CHANNEL,text="Restart Successfully ✓\nKuttu Bot 2 💫\n2db 👀")
        print("Og Eva Re-editeD 2 db Using Feature⚡")

        client = webserver.AppRunner(await bot_run())
        await client.setup()
        bind_address = "0.0.0.0"
        await webserver.TCPSite(client, bind_address,
        PORT_CODE).start()

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")
    
    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            for message in messages:
                yield message
                current += 1


app = Bot()
app.run()
