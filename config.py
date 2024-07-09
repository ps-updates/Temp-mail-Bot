import re, os, time
from dotenv import load_dotenv
load_dotenv("config.env")
id_pattern = re.compile(r'^.\d+$') 

class Config(object):
    # pyrogram client config
    API_ID    = os.environ.get("API_ID", "")
    API_HASH  = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "") 
   
    # database config get this from mongodb
    DB_NAME = os.environ.get("DB_NAME","Cluster0")     
    DB_URL  = os.environ.get("DB_URL","")
 
    # other configs
    BOT_UPTIME  = time.time()
    #start pic url this image will shown in start command get this from @DX_telegraphbot
    START_PIC   = os.environ.get("START_PIC", "")
    ADMIN       = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '').split()]
    #the channel which need to force subscribed, channel startswith -100
    AUTH_CHANNEL = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('AUTH_CHANNEL', '').split()]
    #the log channel id must start in -100 this channel will be were the bot send logs
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", None))

    # wes response configuration
    #if your bot is web required give True or else False
    WEBHOOK = bool(os.environ.get("WEBHOOK", True))
    PORT = int(os.environ.get("PORT", "8080"))
    #the interval time to ping server
    PING_INTERVAL = int(os.environ.get("PING_INTERVAL", "120"))
    #if your bot is running with web cmd pls copy the web link to ping server not down in 1 minutes
    PING_WEB = os.environ.get("PING_WEB", "") 

class Txt(object):

    START_TXT = """<b>🤖ᴛᴇᴍᴘ ᴍᴀɪʟ ɢᴇɴᴇʀᴀᴛᴏʀ ʙᴏᴛ</b>
<b>_____________________________________</b>
<b><i>✏️ ᴏɴᴇ-ᴛɪᴍᴇ ᴍᴀɪʟ ꜰʀᴏᴍ ᴛᴇᴍᴘᴍᴀɪʟ.
ᴘʟᴜs ᴡɪʟʟ sᴀᴠᴇ ʏᴏᴜ ꜰʀᴏᴍ sᴘᴀᴍ ᴀɴᴅ ᴘʀᴏᴍᴏᴛɪᴏɴᴀʟ ᴇᴍᴀɪʟ ɴᴇᴡsʟᴇᴛᴛᴇʀs.
ᴅɪsᴘᴏsᴀʙʟᴇ ᴍᴀɪʟ sᴇʀᴠɪᴄᴇ ꜰᴏʀ ᴀɴᴏɴʏᴍᴏᴜs ᴜsᴇ ɪs ᴘʀᴏᴠɪᴅᴇᴅ ꜰʀᴇᴇ ᴏꜰ ᴄʜᴀʀɢᴇ.
______________________________________</i></b> 
©️ ᴅᴇᴠ :{}
<b>©️ ɢʀᴏᴜᴘ : <a href="https://t.me/premiumyt124">sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ</a>
______________________________________</b>"""
