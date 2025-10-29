import aiohttp
import asyncio
import logging
from datetime import datetime
from info import LOG_CHANNEL, URL

class UptimeKeeperService:
    def __init__(self, client=None):
        self.client = client
        self.last_status_time = datetime.now()
        self.session = None
        self.is_running = False
        self.status_interval = 21600  # 6 hours in seconds
        self.ping_interval = 240      # 4 minutes in seconds

    async def start(self):
        """Start the uptime keeper service."""
        if self.is_running:
            return
        
        self.is_running = True
        self.session = aiohttp.ClientSession()
        
        while self.is_running:
            try:
                # Send ping to prevent sleep
                if URL and URL != "https://your-app-name.onrender.com":
                    try:
                        async with self.session.get(f"{URL}/health") as resp:
                            if resp.status == 200:
                                logging.info("Health check successful")
                            else:
                                logging.warning(f"Health check failed with status: {resp.status}")
                    except Exception as e:
                        logging.warning(f"Health check failed: {str(e)}")

                # Send status message if enough time has passed
                current_time = datetime.now()
                if self.client and (current_time - self.last_status_time).total_seconds() >= self.status_interval:
                    try:
                        status_msg = (
                            "🤖 Bot Status Update\n"
                            f"🕒 Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                            "✅ Status: Running"
                        )
                        await self.client.send_message(LOG_CHANNEL, status_msg)
                        self.last_status_time = current_time
                    except Exception as e:
                        logging.error(f"Failed to send status message: {str(e)}")

            except Exception as e:
                logging.error(f"UptimeKeeper error: {str(e)}")
            
            await asyncio.sleep(self.ping_interval)

    async def stop(self):
        """Stop the uptime keeper service."""
        self.is_running = False
        if self.session:
            await self.session.close()
            self.session = None
