import os, asyncio, logging, random, re, json, base64, sys, time, psutil
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, PeerIdInvalid, FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.ia_filterdb import Media, Media2, get_file_details, unpack_new_file_id
from database.users_chats_db import db
from info import CHANNELS, REACTIONS, ADMINS, AUTH_CHANNEL, LOG_CHANNEL, PICS, BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT
from utils import get_settings, get_size, is_subscribed, save_group_settings, temp
from database.connections_mdb import active_connection
logger = logging.getLogger(__name__)
from datetime import datetime, timedelta
from plugins.pm_filter import auto_filter

BATCH_FILES = {}
REACTIONS = ["🤝", "😇", "🤗", "😍", "👍", "🎅", "😐", "🥰", "🤩", "😱", "🤣", "😘", "👏", "😛", "😈", "🎉", "⚡️", "🫡", "🤓", "😎", "🏆", "🔥", "🤭", "🌚", "🆒", "👻", "😁"] #don't add any emoji because tg not support all emoji reactions


@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message: Message):
    user_id = message.from_user.id
    try:
        await message.react(emoji=random.choice(REACTIONS), big=True) #reaction for start
    except:
        pass
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
            [InlineKeyboardButton('➕ Add Me To Your Groups ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')],
            [InlineKeyboardButton('© Dᴍᴄᴀ', callback_data='dmca')]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(
            script.START_TXT.format(
                message.from_user.mention if message.from_user else message.chat.title,
                temp.U_NAME,
                temp.B_NAME
            ),
            reply_markup=reply_markup
        )
        await asyncio.sleep(2)

        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            await client.send_message(
                LOG_CHANNEL,
                script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown")
            )
            await db.add_chat(message.chat.id, message.chat.title)
        return

    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(
            LOG_CHANNEL,
            script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention)
        )

    if not message.text or len(message.text.split()) != 2:
        buttons = [
            [InlineKeyboardButton('➕ Add Me To Your Groups ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')],
            [
                InlineKeyboardButton('ℹ️ Help', callback_data='help'),
                InlineKeyboardButton('😊 About', callback_data='about')
            ],[
                InlineKeyboardButton('© Dᴍᴄᴀ', callback_data='dmca')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await asyncio.sleep(1)
        clsnt = await client.send_message(
            chat_id=message.chat.id,
            text="<blockquote>❗️Send Movie Name and Year Correctly 👍📌</blockquote>"
        )
        await asyncio.sleep(120)
        await clsnt.delete()
        return
    invite_links = await is_subscribed(client, query=message)
    if AUTH_CHANNEL and len(invite_links) >= 1:
        #this is written by tg: @programcrasher
        btn = []
        for chnl_num, link in enumerate(invite_links, start=1):
            if chnl_num == 1:
                channel_num = "1sᴛ"
            elif chnl_num == 2:
                channel_num = "2ɴᴅ"
            elif chnl_num == 3:
                channel_num = "3ʀᴅ"
            else:
                channel_num = str(chnl_num)+"ᴛʜ"
            btn.append([
                InlineKeyboardButton(f"❆ Jᴏɪɴ {channel_num} Cʜᴀɴɴᴇʟ ❆", url=link)
            ])

        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                pre = 'checksubp' if kk == 'filep' else 'checksub' 
                btn.append([InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ", callback_data=f"{pre}#{file_id}")])
            except (IndexError, ValueError):
                btn.append([InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
        authdel=await client.send_message(
            chat_id=message.from_user.id,
            text="**Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ɪɴ ᴏᴜʀ Bᴀᴄᴋ-ᴜᴘ ᴄʜᴀɴɴᴇʟs ɢɪᴠᴇɴ ʙᴇʟᴏᴡ sᴏ ʏᴏᴜ ᴅᴏɴ'ᴛ ɢᴇᴛ ᴛʜᴇ ᴍᴏᴠɪᴇ ғɪʟᴇ...\n\nIғ ʏᴏᴜ ᴡᴀɴᴛ ᴛʜᴇ ᴍᴏᴠɪᴇ ғɪʟᴇ, ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ɢɪᴠᴇɴ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴀɴᴅ ᴊᴏɪɴ ᴏᴜʀ ʙᴀᴄᴋ-ᴜᴘ ᴄʜᴀɴɴᴇʟs, ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ '↻ Tʀʏ Aɢᴀɪɴ' ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ...\n\nTʜᴇɴ ʏᴏᴜ ᴡɪʟʟ ɢᴇᴛ ᴛʜᴇ ᴍᴏᴠɪᴇ ғɪʟᴇs...**",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
            )
        await asyncio.sleep(33)
        await authdel.delete()
        return
        
        # etc.py link feature !!!>>> import pmfilter autofilter fn()
    if len(message.command) == 2 and message.command[1].startswith('getfile'):
        searches = message.command[1].split("-", 1)[1] 
        search = searches.replace('-',' ')
        message.text = search 
        await auto_filter(client, message) 
        return
        
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [
            [InlineKeyboardButton('➕ Add Me To Your Groups ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')],
            [
                InlineKeyboardButton('ℹ️ Help', callback_data='help'),
                InlineKeyboardButton('😊 About', callback_data='about')
            ],[
                InlineKeyboardButton('© Dᴍᴄᴀ', callback_data='dmca')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""
    if data.split("-", 1)[0] == "BATCH":
        sts = await message.reply("Please wait")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)
        if not msgs:
            file = await client.download_media(file_id)
            try: 
                with open(file) as file_data:
                    msgs=json.loads(file_data.read())
            except:
                await sts.edit("FAILED")
                return await client.send_message(LOG_CHANNEL, "UNABLE TO OPEN FILE.")
            os.remove(file)
            BATCH_FILES[file_id] = msgs
        for msg in msgs:
            title = msg.get("title")
            size=get_size(int(msg.get("size", 0)))
            f_caption=msg.get("caption", "")
            if BATCH_FILE_CAPTION:
                try:
                    f_caption=BATCH_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.exception(e)
                    f_caption=f_caption
            if f_caption is None:
                f_caption = f"{title}"
            try:
                m=await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    )
                # Calculate deletion time: current time + 10 minutes
                now = datetime.now()
                delete_time = now + timedelta(minutes=10)
                formatted_delete_time = delete_time.strftime("%d-%m-%Y %I:%M %p")  # Format: DD-MM-YYYY HH:MM AM/PM
    
                k=f"<blockquote><b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\n⚠️ File will be deleted in 10 Mins\n🗑 Deleting at: {formatted_delete_time}\n\n📌 Save or forward it.\n\n<b><i>ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs ᴏʀ ᴀɴʏ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ.</i></b></blockquote>"
                await asyncio.sleep(600)
                await m.delete()
                await k.edit_text("<b>✅ Yᴏᴜʀ File ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ</b>") 
                return
            except FloodWait as e:
                await asyncio.sleep(e.x)
                logger.warning(f"Floodwait of {e.x} sec.")
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    )
            except Exception as e:
                logger.warning(e, exc_info=True)
                continue
            await asyncio.sleep(1) 
        await sts.delete()
        return
    elif data.split("-", 1)[0] == "DSTORE":
        sts = await message.reply("Please wait")
        b_string = data.split("-", 1)[1]
        decoded = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("ascii")
        try:
            f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
        except:
            f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
            protect = "/pbatch" if PROTECT_CONTENT else "batch"
        diff = int(l_msg_id) - int(f_msg_id)
        async for msg in client.iter_messages(int(f_chat_id), int(l_msg_id), int(f_msg_id)):
            if msg.media:
                media = getattr(msg, msg.media.value)
                if BATCH_FILE_CAPTION:
                    try:
                        f_caption=BATCH_FILE_CAPTION.format(file_name=getattr(media, 'file_name', ''), file_size=getattr(media, 'file_size', ''), file_caption=getattr(msg, 'caption', ''))
                    except Exception as e:
                        logger.exception(e)
                        f_caption = getattr(msg, 'caption', '')
                else:
                    media = getattr(msg, msg.media.value)
                    file_name = getattr(media, 'file_name', '')
                    f_caption = getattr(msg, 'caption', file_name)
                try:
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            elif msg.empty:
                continue
            else:
                try:
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            await asyncio.sleep(1) 
        return await sts.delete()
        

    files_ = await get_file_details(file_id)           
    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        try:
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                protect_content=True if pre == 'filep' else False,
                )
            # Calculate deletion time: current time + 10 minutes
            now = datetime.now()
            delete_time = now + timedelta(minutes=10)
            formatted_delete_time = delete_time.strftime("%d-%m-%Y %I:%M %p")  # Format: DD-MM-YYYY HH:MM AM/PM
    
            k=f"<blockquote><b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\n⚠️ File will be deleted in 10 Mins\n🗑 Deleting at: {formatted_delete_time}\n\n📌 Save or forward it.\n\n<b><i>ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs ᴏʀ ᴀɴʏ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ.</i></b></blockquote>"
            await asyncio.sleep(600)
            await m.delete()
            await k.edit_text("<b>✅ Yᴏᴜʀ File ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ</b>") 
            return
            filetype = msg.media
            file = getattr(msg, filetype.value)
            title = file.file_name
            size=get_size(file.file_size)
            f_caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
                except:
                    return
            await msg.edit_caption(f_caption)
            return
        except:
            pass
        return await message.reply('No such file exist.')
    files = files_[0]
    title = files.file_name
    size=get_size(files.file_size)
    f_caption=files.caption
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
        except Exception as e:
            logger.exception(e)
            f_caption=f_caption
    if f_caption is None:
        f_caption = f"{files.file_name}"
    m=await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=True if pre == 'filep' else False,
        )
    # Calculate deletion time: current time + 10 minutes
    now = datetime.now()
    delete_time = now + timedelta(minutes=10)
    formatted_delete_time = delete_time.strftime("%d-%m-%Y %I:%M %p")  # Format: DD-MM-YYYY HH:MM AM/PM
    
    k=f"<blockquote><b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>\n\n⚠️ File will be deleted in 10 Mins\n🗑 Deleting at: {formatted_delete_time}\n\n📌 Save or forward it.\n\n<b><i>ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ ʏᴏᴜʀ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs ᴏʀ ᴀɴʏ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ.</i></b></blockquote>"                
    await asyncio.sleep(600)
    await m.delete()
    await k.edit_text("<b>✅ Yᴏᴜʀ File ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ</b>") 
    return     
                    

@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
           
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Pʀᴏᴄᴇssɪɴɢ...⏳", quote=True)
    else:
        await message.reply('Rᴇᴘʟʏ ᴛᴏ ғɪʟᴇ ᴡɪᴛʜ /delete ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('Tʜɪs ɪs ɴᴏᴛ sᴜᴘᴘᴏʀᴛᴇᴅ ғɪʟᴇ ғᴏʀᴍᴀᴛ')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)
    if await Media.count_documents({'file_id': file_id}):
        result = await Media.collection.delete_one({
            '_id': file_id,
        })
    else:
        result = await Media2.collection.delete_one({
            '_id': file_id,
        })
    if result.deleted_count:
        await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ')
        else:
            result = await Media2.collection.delete_many({
                'file_name': file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ')
            else:
                # files indexed before https://github.com/EvamariaTG/EvaMaria/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf#diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39 
                # have original file name.
                result = await Media.collection.delete_many({
                    'file_name': media.file_name,
                    'file_size': media.file_size,
                    'mime_type': media.mime_type
                })
                if result.deleted_count:
                    await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ')
                else:
                    result = await Media2.collection.delete_many({
                        'file_name': media.file_name,
                        'file_size': media.file_size,
                        'mime_type': media.mime_type
                    })
                    if result.deleted_count:
                        await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ')
                    else:
                        await msg.edit('Fɪʟᴇ ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ')

@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'This will delete all indexed files.\nDo you want to continue??',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="YES", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="CANCEL", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await Media2.collection.drop()
    await message.answer('Piracy Is Crime')
    await message.message.edit('Succesfully Deleted All The Indexed Files.')


@Client.on_message(filters.command('settings'))
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You are anonymous admin. Use /connect {message.chat.id} in PM")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return

    settings = await get_settings(grp_id)

    if settings is not None:
        buttons = [
            [
                InlineKeyboardButton(
                    'Filter Button',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'Single' if settings["button"] else 'Double',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Bot PM',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["botpm"] else '❌ No',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'File Secure',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["file_secure"] else '❌ No',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'IMDB',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["imdb"] else '❌ No',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Spell Check',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["spell_check"] else '❌ No',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Welcome',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["welcome"] else '❌ No',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await message.reply_text(
            text=f"<b>Change Your Settings for {title} As Your Wish ⚙</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=message.id
        )

@Client.on_message(filters.command("restart") & filters.user(ADMINS))
async def stop_button(bot, message):
    msg = await bot.send_message(text="**𝖡𝗈𝗍 𝖨𝗌 𝖱𝖾𝗌𝗍𝖺𝗋𝗍𝗂𝗇𝗀...🪄**", chat_id=message.chat.id)       
    await asyncio.sleep(2.5)
    await msg.edit("**𝖡𝗈𝗍 𝖱𝖾𝗌𝗍𝖺𝗋𝗍𝖾𝖽 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒 ! 𝖱𝖾𝖺𝖽𝗒 𝖳𝗈 𝖬𝗈𝗏𝖾 𝖮𝗇 💯**")
    os.execl(sys.executable, sys.executable, *sys.argv)

BOT_START_TIME = time.time()

def format_uptime_short(seconds: int) -> str:
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, sec = divmod(rem, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}hr")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if sec > 0 or not parts:
        parts.append(f"{sec}s")

    return " ".join(parts)

@Client.on_message(filters.command("usage"))
async def usage(client, message):
    uptime_seconds = int(time.time() - BOT_START_TIME)
    uptime_str = format_uptime_short(uptime_seconds)

    cpu_percent = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    mem_used = round(mem.used / (1024 ** 2), 2)
    mem_total = round(mem.total / (1024 ** 2), 2)
    mem_percent = mem.percent
    disk = psutil.disk_usage('/')
    disk_used = round(disk.used / (1024 ** 3), 2)
    disk_total = round(disk.total / (1024 ** 3), 2)
    disk_percent = disk.percent

    text = (
        "**📊 Bot Resource Usage:**\n\n"

        f"⏱️ Uptime: `{uptime_str}`\n"
        f"🖥️ CPU Usage: `{cpu_percent}%`\n"
        f"🧠 Memory: `{mem_used}MB / {mem_total}MB ({mem_percent}%)`\n"
        f"💾 Disk: `{disk_used}GB / {disk_total}GB ({disk_percent}%)`"
    )
    await message.reply_text(text)
