from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
import os, sys, time, asyncio, logging, datetime
from config import Config , Txt
from database import db

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

async def is_subscribed(bot, query, channel):
    btn = []
    for id in channel:
        chat = await bot.get_chat(int(id))
        try:
            await bot.get_chat_member(id, query.from_user.id)
        except UserNotParticipant:
            btn.append([InlineKeyboardButton(f'Join {chat.title}', url=chat.invite_link)])
        except Exception as e:
            pass
    return btn

@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user = message.from_user
    await db.add_user(client, message)

    button = InlineKeyboardMarkup([
        [InlineKeyboardButton(text='sᴇᴛ ᴜsᴇʀɴᴀᴍᴇ', url=f'tg://user?id={user.id}')],
        [InlineKeyboardButton(text='done', callback_data='/start')]])

    if not user.username:
        await message.reply_text(
            f'<b>ᴡᴇʟᴄᴏᴍᴇ {user.mention}\n\n⚠️ ᴘʟᴇᴀsᴇ sᴇᴛ ʏᴏᴜʀ ᴛᴇʟᴇɢʀᴀᴍ ᴜsᴇʀɴᴀᴍᴇ ʙᴇꜰᴏʀᴇ ᴜsɪɴɢ ᴛʜɪs ʙᴏᴛ</b>',
            reply_markup=button, parse_mode=ParseMode.HTML
        )
        return
        
    if Config.AUTH_CHANNEL:
        try:
            btn = await is_subscribed(client, message, AUTH_CHANNEL)
            if btn:
                username = (await client.get_me()).username
                if message.command[1]:
                    btn.append([InlineKeyboardButton("♻️ Try Again ♻️", url=f"https://t.me/{username}?start={message.command[1]}")])
                else:
                    btn.append([InlineKeyboardButton("♻️ Try Again ♻️", url=f"https://t.me/{username}?start=true")])
                await message.reply_text(text=f"<b>👋 Hello {message.from_user.mention},\n\nPlease join the channel then click on try again button. 😇</b>", reply_markup=InlineKeyboardMarkup(btn))
                return
        except Exception as e:
            print(e)
   
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton('📧 ɢᴇɴᴇʀᴀᴛᴇ ᴇᴍᴀɪʟ', callback_data='generate_email')],
        [InlineKeyboardButton('📮 ᴄʜᴇᴄᴋ ɪɴʙᴏx', callback_data='check_inbox')],
        [InlineKeyboardButton('📊 sᴛᴀᴛɪsᴛɪᴄs', callback_data='statistics')],
        [InlineKeyboardButton('📞 sᴜᴘᴘᴏʀᴛ', callback_data='support')]
    ])
    if Config.START_PIC:
        await message.reply_photo(
                Config.START_PIC, 
                caption=Txt.START_TXT,
                parse_mode=ParseMode.HTML, reply_markup=keyboard
                )
    else:
        await message.reply_text(
                text=Txt.START_TXT, 
                parse_mode=ParseMode.HTML, 
                reply_markup=keyboard,
                disable_web_page_preview=True
                )

@Client.on_callback_query(filters.regex('generate_email'))
async def generate_email(client, query):
    user_id = query.from_user.id
    processing_message = await query.message.reply("⏳")
    texts = ["⏳ g", "⏳ ge", "⏳ gen", "⏳ gener", "⏳ genera", "⏳ generat", "⏳ generati", "⏳ generatin", "⏳ generating", "⏳ generating.", "⏳ generating..", "⏳ generating..."]
    
    for text in texts:
        await processing_message.edit(text=text)
        await asyncio.sleep(0.5)  # Adjust the delay as necessary

    cur_time = int(time.time())
    user_data = await db.get_data(user_id, ["limit", "used"])
    limit = user_data["limit"]
    used = user_data["used"]
    
    if used is None:
        used = 0
    elif cur_time - (limit or 0) > 24 * 60 * 60:
        used = 0
        
    if limit is None or cur_time - limit > 24 * 60 * 60 or used < 100:
        await db.save_data(user_id, {"limit": cur_time, "used": int(used) + 1})
        
        response = requests.post("https://api.internal.temp-mail.io/api/v3/email/new", json={'min_name_length': 10, 'max_name_length': 10})
        content = response.json()
        c1 = content['email']
        c2 = content['token']
        link = f"https://temp-mail.io/en/email/{c1}/token/{c2}?utm_campaign=TempMailBot&utm_content=email_info&utm_medium=organic&utm_source=telegram-bot"
        
        button = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="🌐 ᴠɪᴇᴡ ᴍᴇssᴀɢᴇ ɪɴ ʙʀᴏᴡsᴇʀ [ ᴛᴇᴍᴘ-ᴍᴀɪʟ.ɪᴏ ]", url=link)],
            [InlineKeyboardButton(text="🗑️ ᴅᴇʟᴇᴛᴇ", callback_data=f"/del {c1} {c2}")]
        ])
        
        await processing_message.edit(
            text=f"*📧 ʏᴏᴜʀ ᴛᴇᴍᴘᴏʀᴀʀʏ ᴇᴍᴀɪʟ ᴀᴅᴅʀᴇss:*\n{c1}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=button
        )
        
        await db.save_data(user_id, {"email": c1, "token": c2})
    else:
        await processing_message.edit(
            text="⚠️ *ʏᴏᴜʀ ᴇᴍᴀɪʟ ɢᴇɴᴇʀᴀᴛᴇ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ\nᴛʀʏ ᴀɢᴀɪɴ ᴀꜰᴛᴇʀ 24 ʜᴏᴜʀs*",
            parse_mode=ParseMode.MARKDOWN
        )

@Client.on_callback_query(filters.regex('check_inbox'))
async def check_email(client, query):
    user_id = query.from_user.id
    await client.send_chat_action(chat_id=query.message.chat.id, action="typing")
    user_data = await db.get_data(user_id, ["email"])
    at = user_data["email"]
    count = 0

    if at is None:
        await query.message.reply("*❌ ᴘʟᴇᴀsᴇ ᴄʀᴇᴀᴛᴇ ᴀɴ ᴇᴍᴀɪʟ ꜰɪʀsᴛ*", parse_mode=ParseMode.MARKDOWN)
    else:
        response = requests.get(f"https://api.internal.temp-mail.io/api/v3/email/{at}/messages")
        result = response.json()
        
        if len(result) < 1:
            await query.message.reply("*❌ ɴᴏ ᴍᴇssᴀɢᴇs ᴡᴇʀᴇ ʀᴇᴄᴇɪᴠᴇᴅ....*", parse_mode=ParseMode.MARKDOWN)
        else:
            for i in result:
                fr = i['from']
                email_id = i['id']
                date = i['created_at']
                sub = i['subject']
                dt = i['body_text']
                to = i['to']
                count += 1
                button = InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="🌐 ᴠɪᴇᴡ ᴍᴇssᴀɢᴇ ɪɴ ʙʀᴏᴡsᴇʀ [ ᴛᴇᴍᴘ-ᴍᴀɪʟ.ɪᴏ ]", url=f"https://temp-mail.io/en/message/{email_id}")]
                ])
                await query.message.reply_text(
                    text=f"*📮 ɪɴʙᴏx #{count}\n🆔️ ɪᴅ : {email_id}\n🗓️ ᴅᴀᴛᴇ : {date.split('T')[0]}\n✈ ᴛᴏ : {to}\n🔰 sᴜʙᴊᴇᴄᴛ : {sub}\n📌 ꜰʀᴏᴍ : {fr}*\n*💬 ᴍᴇssᴀɢᴇ : {dt}*",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=button
                )

@Client.on_callback_query(filters.regex('statistics'))
async def show_statistics(client, query):
    currentTime = readable_time((time.time() - StartTime))
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    botstats = f'<b>Bot Uptime:</b> {currentTime}\n' \
            f'<b>Total disk space:</b> {total}\n' \
            f'<b>Used:</b> {used}  ' \
            f'<b>Free:</b> {free}\n\n' \
            f'📊Data Usage📊\n<b>Upload:</b> {sent}\n' \
            f'<b>Down:</b> {recv}\n\n' \
            f'<b>CPU:</b> {cpuUsage}% ' \
            f'<b>RAM:</b> {memory}% ' \
            f'<b>Disk:</b> {disk}%'    
    await query.answer("Fetching MongoDb DataBase...")
    await asyncio.sleep(2)
    await query.reply_text(botstats, parse_mode=ParseMode.HTML)

@Client.on_callback_query(filters.regex('support'))
async def support(client, query):
    user_id = query.from_user.id
    await client.delete_messages(chat_id=query.message.chat.id, message_ids=query.message.message_id)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text='❌ᴄᴀɴᴄᴇʟ', callback_data='cancel_support')]
    ])
    await query.message.reply_text(
        "<b>📞 ʏᴏᴜ ᴀʀᴇ ɴᴏᴡ ɪɴ ᴅɪʀᴇᴄᴛ ᴄᴏɴᴛᴀᴄᴛ ᴡɪᴛʜ ᴏᴜʀ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ</b>\n\n<i>ʏᴏᴜ ᴄᴀɴ sᴇɴᴅ ʜᴇʀᴇ ᴀɴʏ ᴍᴇssᴀɢᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sᴜʙᴍɪᴛ, ᴛʜᴇ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴡɪʟʟ ʀᴇᴄᴇɪᴠᴇ ɪᴛ ᴀɴᴅ sᴇɴᴅ ᴀɴ ᴀɴsᴡᴇʀ ᴅɪʀᴇᴄᴛʟʏ ʜᴇʀᴇ ɪɴ ᴄʜᴀᴛ!</i>",
        reply_markup=keyboard, parse_mode=ParseMode.HTML
    )
    await Client.set_user_state(user_id, "support_chat")

@Client.on_callback_query(filters.regex('cancel_support'))
async def cancel_support(client, query):
    await client.delete_messages(chat_id=query.message.chat.id, message_ids=query.message.message_id)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton('📧 ɢᴇɴᴇʀᴀᴛᴇ ᴇᴍᴀɪʟ', callback_data='generate_email')],
        [InlineKeyboardButton('📮 ᴄʜᴇᴄᴋ ɪɴʙᴏx', callback_data='check_inbox')],
        [InlineKeyboardButton('📊 sᴛᴀᴛɪsᴛɪᴄs', callback_data='statistics')],
        [InlineKeyboardButton('📞 sᴜᴘᴘᴏʀᴛ', callback_data='support')]
    ])
    await query.message.reply_photo(photo="https://graph.org/file/557d82c251df20c24495a.jpg", caption=Txt.START_TXT,
              parse_mode=ParseMode.HTML, reply_markup=keyboard)
    await Client.set_user_state(query.from_user.id, None)

@Client.on_message(filters.user_state("support_chat"))
async def handle_support_message(client, message):
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('↩️ ʀᴇᴘʟʏ ᴜsᴇʀ', callback_data=f'/replyUser {message.chat.id}')]
    ])
    await client.send_message(
        chat_id=Config.ADMIN, 
        text=f"*📩 ɴᴇᴡ sᴜᴘᴘᴏʀᴛ ᴍᴇssᴀɢᴇ ꜰʀᴏᴍ:\n\n➡️ ɴᴀᴍᴇ: {message.from_user.first_name}\n➡️ ᴜsᴇʀɴᴀᴍᴇ: @{message.from_user.username}\n➡️ ɪᴅ:* `{message.chat.id}`\n\n📝 *ᴍᴇssᴀɢᴇ: {message.text}*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=markup
    )
    await message.reply_text(f"*✅ ᴍᴇssᴀɢᴇ sᴇɴᴛ ᴛᴏ ᴛʜᴇ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ:* _{message.text}_", parse_mode=ParseMode.MARKDOWN)
    await Client.set_user_state(message.from_user.id, None)

@Client.on_callback_query(filters.regex('/replyUser'))
async def reply_user(client, query):
    admin = query.from_user.id
    if admin in Config.ADMIN:
        await query.message.reply_text("*➡️ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ ꜰᴏʀ ᴜsᴇʀ*", parse_mode=ParseMode.MARKDOWN)
        await Client.set_user_state(admin, "reply_user", query.data.split()[1])
    else:
        await query.message.reply_text("<b>Sorry, this command is only available to administrators.</b>", parse_mode=ParseMode.HTML)

@Client.on_message(filters.user_state("reply_user"))
async def handle_reply_user(client, message):
    options = message.chat.state_params
    await client.send_message(chat_id=options,
                text=f"*📩 ɴᴇᴡ sᴜᴘᴘᴏʀᴛ ᴍᴇssᴀɢᴇ ꜰʀᴏᴍ ᴀᴅᴍɪɴ:\n\n📝 ᴍᴇssᴀɢᴇ:* _{message.text}_", parse_mode="MARKDOWN")
    await message.reply_text(
        f"*↩️ ʀᴇᴘʟʏ sᴇɴᴛ ᴛᴏ ᴜsᴇʀ:* _{message.text}_", parse_mode="MARKDOWN")
    await Client.set_user_state(message.chat.id, None)

@Client.on_message(filters.command("broadcast") & filters.user(Config.ADMIN) & filters.reply)
async def broadcast_handler(client: Client, message: Message):
    await client.send_message(Config.LOG_CHANNEL, f"{message.from_user.mention} or {message.from_user.id} Iꜱ ꜱᴛᴀʀᴛᴇᴅ ᴛʜᴇ Bʀᴏᴀᴅᴄᴀꜱᴛ......")
    all_users = await db.get_all_users()
    broadcast_msg = message.reply_to_message
    sts_msg = await message.reply_text("Bʀᴏᴀᴅᴄᴀꜱᴛ Sᴛᴀʀᴛᴇᴅ..!") 
    done = 0
    failed = 0
    success = 0
    start_time = time.time()
    total_users = await db.total_users_count()
    async for user in all_users:
        sts = await send_msg(user['_id'], broadcast_msg)
        if sts == 200:
           success += 1
        else:
           failed += 1
        if sts == 400:
           await db.delete_user(user['_id'])
        done += 1
        if not done % 20:
           await sts_msg.edit(f"Bʀᴏᴀᴅᴄᴀꜱᴛ Iɴ Pʀᴏɢʀᴇꜱꜱ: \nTᴏᴛᴀʟ Uꜱᴇʀꜱ {total_users} \nCᴏᴍᴩʟᴇᴛᴇᴅ: {done} / {total_users}\nSᴜᴄᴄᴇꜱꜱ: {success}\nFᴀɪʟᴇᴅ: {failed}")
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(f"Bʀᴏᴀᴅᴄᴀꜱᴛ Cᴏᴍᴩʟᴇᴛᴇᴅ: \nCᴏᴍᴩʟᴇᴛᴇᴅ Iɴ `{completed_in}`.\n\nTᴏᴛᴀʟ Uꜱᴇʀꜱ {total_users}\nCᴏᴍᴩʟᴇᴛᴇᴅ: {done} / {total_users}\nSᴜᴄᴄᴇꜱꜱ: {success}\nFᴀɪʟᴇᴅ: {failed}")
           
async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await send_msg(user_id, message)
    except InputUserDeactivated:
        logger.info(f"{user_id} : Dᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ")
        return 400
    except UserIsBlocked:
        logger.info(f"{user_id} : Bʟᴏᴄᴋᴇᴅ Tʜᴇ Bᴏᴛ")
        return 400
    except PeerIdInvalid:
        logger.info(f"{user_id} : Uꜱᴇʀ Iᴅ Iɴᴠᴀʟɪᴅ")
        return 400
    except Exception as e:
        logger.error(f"{user_id} : {e}")
        return 500
