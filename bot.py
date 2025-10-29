import sys
import glob
import signal
import importlib
from pathlib import Path
from pyrogram import Client, idle, __version__
from pyrogram.raw.all import layer
from pyrogram.types import BotCommand
import time
from pyrogram.errors import FloodWait
import asyncio
from datetime import date, datetime
import pytz
from aiohttp import web
from dotenv import load_dotenv
import os

# Set UTF-8 encoding for Windows console
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.platform.startswith('win'):
    import codecs
    codecs.register(lambda name: codecs.lookup('utf-8') if name == 'cp65001' else None)

# Load environment variables from .env file
load_dotenv()
print(f"DATABASE_URI: {os.getenv('DATABASE_URI')}")

from database.ia_filterdb import Media, Media2
from database.users_chats_db import db
from info import *
from utils import temp
from Script import script
from plugins import web_server, check_expired_premium, keep_alive
from dreamxbotz.Bot import dreamxbotz
from dreamxbotz.util.keepalive import ping_server
from dreamxbotz.Bot.clients import initialize_clients
from PIL import Image
Image.MAX_IMAGE_PIXELS = 500_000_000

import logging
import logging.config

# Complete Bot commands definition with all commands
bot_commands = [
    # Basic Commands
    BotCommand("start", "Sᴛᴀʀᴛ Mᴇ Bᴀʙʏ"),
    BotCommand("stats", "Gᴇᴛ Bᴏᴛ Sᴛᴀᴛs"),
    BotCommand("alive", "Cʜᴇᴄᴋ Bᴏᴛ Aʟɪᴠᴇ ᴏʀ Nᴏᴛ"),
    BotCommand("settings", "ᴄʜᴀɴɢᴇ sᴇᴛᴛɪɴɢs"),
    BotCommand("id", "ɢᴇᴛ ɪᴅ ᴛᴇʟᴇɢʀᴀᴍ"),
    BotCommand("info", "Gᴇᴛ Usᴇʀ ɪɴғᴏ"),
    BotCommand("del_msg", "ʀᴇᴍᴏᴠᴇ ғɪʟᴇ ɴᴀᴍᴇ ᴄᴏʟʟᴇᴄᴛɪᴏɴ ɴᴏтɪғɪᴄᴀᴛɪᴏɴ"),
    BotCommand("movie_update", "ᴏɴ ᴏғғ ᴀᴄᴄᴏʀᴅɪɴɢ ʏᴏᴜʀ ɴᴇᴇᴅᴇᴅ"),
    BotCommand("pm_search", "ᴘᴍ sᴇᴀʀᴄʜ ᴏɴ ᴏғғ ᴀᴄᴄᴏʀᴅɪɴɢ ʏᴏᴜʀ ɴᴇᴇᴅᴇᴅ"),
    BotCommand("trendlist", "Gᴇᴛ Tᴏᴘ Tʀᴀɴᴅɪɴɢ Sᴇᴀʀᴄʜ Lɪsᴛ"),
    
    # Admin Commands
    BotCommand("broadcast", "ʙʀᴏᴀᴅᴄᴀsᴛ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴀʟʟ ᴜsᴇʀs"),
    BotCommand("grp_broadcast", "ʙʀᴏᴀᴅᴄᴀsᴛ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴀʟʟ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɢʀᴏᴜᴘs"),
    BotCommand("send", "sᴇɴᴅ ᴍᴇssᴀɢᴇ ᴛᴏ ᴀ ᴘᴀʀᴛɪᴄᴜʟᴀʀ ᴜsᴇʀ"),
    BotCommand("add_premium", "ᴀᴅᴅ ᴀɴʏ ᴜsᴇʀ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ"),
    BotCommand("remove_premium", "ʀᴇᴍᴏᴠᴇ ᴀɴʏ ᴜsᴇʀ ғʀᴏᴍ ᴘʀᴇᴍɪᴜᴍ"),
    BotCommand("premium_users", "ɢᴇᴛ ʟɪsᴛ ᴏғ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs"),
    BotCommand("restart", "ʀᴇsᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ"),
    BotCommand("group_cmd", "ɢʀᴏᴜᴘ ᴄᴏᴍᴍᴀɴᴅ ʟɪsᴛ"),
    BotCommand("admin_cmd", "ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs ʟɪsᴛ"),
    BotCommand("reset_group", "Group Setting Default"),
    BotCommand("trial_reset", "User Trial Reset"),
    
    # Group Admin Commands - NEW
    BotCommand("set_shortner", "sᴇᴛ ʏᴏᴜʀ 1sᴛ sʜᴏʀᴛɴᴇʀ"),
    BotCommand("set_shortner_2", "sᴇᴛ ʏᴏᴜʀ 2ɴᴅ sʜᴏʀᴛɴᴇʀ"),
    BotCommand("set_shortner_3", "sᴇᴛ ʏᴏᴜʀ 3ʀᴅ sʜᴏʀᴛɴᴇʀ"),
    BotCommand("set_tutorial", "sᴇᴛ ʏᴏᴜʀ 1sᴛ ᴛᴜᴛᴏʀɪᴀʟ ᴠɪᴅᴇᴏ"),
    BotCommand("set_tutorial_2", "sᴇᴛ ʏᴏᴜʀ 2ɴᴅ ᴛᴜᴛᴏʀɪᴀʟ ᴠɪᴅᴇᴏ"),
    BotCommand("set_tutorial_3", "sᴇᴛ ʏᴏᴜʀ 3ʀᴅ ᴛᴜᴛᴏʀɪᴀʟ ᴠɪᴅᴇᴏ"),
    BotCommand("set_time", "sᴇᴛ 1sᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ɢᴀᴘ"),
    BotCommand("set_time_2", "sᴇᴛ 2ɴᴅ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ɢᴀᴘ"),
    BotCommand("set_log_channel", "sᴇᴛ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ʟᴏɢ ᴄʜᴀɴɴᴇʟ"),
    BotCommand("set_fsub", "sᴇᴛ ᴄᴜsᴛᴏᴍ ғᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ"),
    BotCommand("remove_fsub", "ʀᴇᴍᴏᴠᴇ ᴄᴜsᴛᴏᴍ ғᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ"),
    BotCommand("details", "ᴄʜᴇᴄᴋ ʏᴏᴜʀ sᴇᴛᴛɪɴɢs")
]

# Function to set bot commands
async def set_bot_commands():
    try:
        await dreamxbotz.set_bot_commands(bot_commands)
        print("✅ Bot commands set successfully!")
        print(f"📋 Total commands registered: {len(bot_commands)}")
        logging.info("Bot commands menu updated successfully!")
    except Exception as e:
        print(f"❌ Error setting bot commands: {e}")
        logging.error(f"Error setting bot commands: {e}")

logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)
logging.getLogger("pymongo").setLevel(logging.WARNING)

botStartTime = time.time()
ppath = "plugins/*.py"
files = glob.glob(ppath)

async def dreamxbotz_start():
    print('\n\nInitalizing DreamxBotz')
    await dreamxbotz.start()
    bot_info = await dreamxbotz.get_me()
    dreamxbotz.username = bot_info.username
    await initialize_clients()
    
    # Set bot commands here after bot starts
    await set_bot_commands()
    
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("DreamxBotz Imported => " + plugin_name)
            
    if ON_HEROKU:
        asyncio.create_task(ping_server()) 
        
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    await Media.ensure_indexes()
    
    if MULTIPLE_DB:
        await Media2.ensure_indexes()
        print("Multiple Database Mode On. Now Files Will Be Save In Second DB If First DB Is Full")
    else:
        print("Single DB Mode On ! Files Will Be Save In First Database")
        
    me = await dreamxbotz.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    temp.B_LINK = me.mention
    dreamxbotz.username = '@' + me.username
    dreamxbotz.loop.create_task(check_expired_premium(dreamxbotz))
    
    logging.info(f"{me.first_name} with Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
    logging.info(LOG_STR)
    logging.info(script.LOGO)
    
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    
    await dreamxbotz.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(temp.B_LINK, today, time))
    
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    dreamxbotz.loop.create_task(keep_alive(dreamxbotz))
    
    async def signal_handler():
        """Handle shutdown gracefully"""
        logging.info("Stop signal received. Performing cleanup...")
        await dreamxbotz.stop()
        sys.exit(0)

    try:
        # Only add signal handlers on Unix-like systems
        if not sys.platform.startswith('win'):
            for sig in (signal.SIGTERM, signal.SIGINT):
                dreamxbotz.loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(signal_handler()))
    except NotImplementedError:
        # Windows doesn't support signal handlers
        pass
    
    await idle()
    
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    while True:
        try:
            loop.run_until_complete(dreamxbotz_start())
            break  
        except FloodWait as e:
            print(f"FloodWait! Sleeping for {e.value} seconds.")
            time.sleep(e.value) 
        except KeyboardInterrupt:
            logging.info('Service Stopped Bye 👋')
            break
