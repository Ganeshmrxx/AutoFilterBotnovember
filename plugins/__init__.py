
from aiohttp import web
from .route import routes
from asyncio import sleep 
from datetime import datetime
from database.users_chats_db import db
from info import LOG_CHANNEL, URL, PORT
import aiohttp
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app

async def start_server():
    """Start the web server for Render deployment."""
    web_app = await web_server()
    await web._run_app(
        web_app,
        host='0.0.0.0',
        port=PORT,
    )

async def check_expired_premium(client):
    while 1:
        data = await db.get_expired(datetime.now())
        for user in data:
            user_id = user["id"]
            await db.remove_premium_access(user_id)
            try:
                user = await client.get_users(user_id)
                await client.send_message(
                    chat_id=user_id,
                    text=f"<b>ʜᴇʏ {user.mention},\n\nʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss ʜᴀs ʙᴇᴇɴ ᴇxᴘɪʀᴇᴅ. ᴛʜᴀɴᴋ ʏᴏᴜ ғᴏʀ ᴜsɪɴɢ ᴏᴜʀ sᴇʀᴠɪᴄᴇ 😁. ᴄʟɪᴄᴋ ᴏɴ /plan ᴛᴏ ᴄʜᴇᴄᴋ ᴏᴜʀ ᴘʟᴀɴs,ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʀᴇ-ᴛᴀᴋᴇ ᴀɢᴀɪɴ</b>"
                )
                await client.send_message(LOG_CHANNEL, text=f"<b>#Premium_Expire\n\nUser name: {user.mention}\nUser id: <code>{user_id}</code>")
            except Exception as e:
                print(e)
            await sleep(0.5)
        await sleep(1)

from .keep_alive import UptimeKeeperService

async def keep_alive(client=None):
    """Keep bot alive by sending periodic pings."""
    uptime_keeper = UptimeKeeperService(client)
    await uptime_keeper.start()

