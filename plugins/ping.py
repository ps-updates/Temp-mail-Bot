from pyrogram import Client,filters
from config import Config
from helper.database import db
from pyrogram.types import Message
import time

@Client.on_message(filters.private & filters.regex("ping"))
async def ping(b, m):
    start_t = time.time()
    ag = await m.reply_text("....")
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await ag.edit(f"Pong!\n{time_taken_s:.3f} ms")

@Client.on_message(filters.command("users") & filters.user(Config.ADMIN))
async def get_stats(bot :Client, message: Message):
    mr = await message.reply('**𝙰𝙲𝙲𝙴𝚂𝚂𝙸𝙽𝙶 𝙳𝙴𝚃𝙰𝙸𝙻𝚂.....**')
    total_users = await db.total_users_count()
    await mr.edit( text=f"❤️‍🔥 TOTAL USER'S = `{total_users}`")
