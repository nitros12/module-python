import asyncio
import aiohttp


class ApiError(Exception):
    def __init__(self, code: int, desc: str):
        self.code = code
        self.desc = desc

    def __str__(self):
        return f"API Error id {self.code}: {self.desc}"


class AnalytiCord:

    base_address = "https://analyticord.solutions"
    login_address = base_address + "/api/botLogin"
    send_address = base_address + "/api/submit"

    def __init__(self,
                 token: str,
                 message_interval: int=60,
                 session: aiohttp.ClientSession=None,
                 loop=None):
        self.token = token
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.session = aiohttp.ClientSession() if session is None else session
        self.message_interval = message_interval

        self.message_lock = asyncio.Lock()
        self.message_count = 0

        self.loop.create_task(self.start())

    async def start(self):
        """Start up analyticord connection.
        Also runs the message updater loop

        :raises: :class:`analyticord.ApiError` on error.
        """
        async with self.session.get(
                AnalytiCord.login_address,
                headers=dict(Authorization=self.token)) as resp:
            if resp.status != 200:
                err = await resp.json()
                code = int(err.get("error", -1))
                desc = err.get("description")
                raise ApiError(code=code, desc=desc)

            self.loop.create_task(self.update_messages_loop())

    async def send(self, event_type: str, data: str):
        """Send data to analiticord.

        :param event_type: Event type to send.
        :param data: Data to send.

        :raises: :class:`analyticord.ApiError` on error.
        """
        async with self.session.post(
                AnalytiCord.send_address,
                data=dict(eventType=event_type, data=data),
                headers=dict(Authorization=self.token)) as resp:
            if resp.status != 200:
                err = await resp.json()
                code = int(err.get("error", -1))
                desc = err.get("description")
                raise ApiError(code=code, desc=desc)

    async def increment_messages(self, *_):
        """Increment the message count.

        This blocks if a message update is occuring at the same time.
        """
        async with self.message_lock:
            self.message_count += 1

    async def update_messages_loop(self):
        while True:
            await asyncio.sleep(self.message_interval)
            if self.message_count:
                async with self.message_lock:
                    await self.send("messages", str(self.message_count))
                    self.message_count = 0

    def hook_bot(self, bot):
        """Hook the on_message events of a discord.py bot."""
        bot.add_listener(self.increment_messages, "on_message")
