import asyncio
import aiohttp
import logging

logger = logging.getLogger("analyticord")


class ApiError(Exception):
    def __init__(self, error: str, description: str, status: int, **extra):
        self.code = error
        self.desc = description
        self.status = status
        self.extra = extra

    def __str__(self):
        return f"API Error id {self.code}: {self.desc} (http code: {self.status}). Extra attrs: {self.extra}"


class AnalytiCord:

    base_address = "https://analyticord.solutions"
    login_address = base_address + "/api/botLogin"
    send_address = base_address + "/api/submit"
    get_address = base_address + "/api/getData"

    def __init__(self,
                 token: str,
                 message_interval: int=60,
                 do_message_loop: bool=True,
                 session: aiohttp.ClientSession=None,
                 loop=None):
        self.token = token
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.session = aiohttp.ClientSession() if session is None else session
        self.message_interval = message_interval
        self.do_message_loop = do_message_loop

        self.message_lock = asyncio.Lock()
        self.message_count = 0

        self.loop.create_task(self.start())

    @property
    def auth(self):
        return {"Authorization": self.token}

    async def start(self):
        """Start up analyticord connection.
        Also runs the message updater loop

        :raises: :class:`analyticord.ApiError` on error.
        """
        async with self.session.get(
                AnalytiCord.login_address,
                headers=self.auth) as resp:
            if resp.status != 200:
                err = await resp.json()
                raise ApiError(status=resp.status, **err)

        if self.do_message_loop:
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
                headers=self.auth) as resp:
            if resp.status != 200:
                err = await resp.json()
                raise ApiError(status=resp.status, **err)

    async def get(self, **attrs) -> dict:
        """Get data from the api.

        :param attrs: Kwarg attributes passed to get request params.

        :return: Tuple of response code and Dict response from api. (status, dict).
        """
        async with self.session.get(
                AnalytiCord.get_address,
                params=attrs,
                headers=self.auth) as resp:
            return (resp.status, await resp.json())

    async def increment_messages(self, *_):
        """Increment the message count.

        This blocks if a message update is occuring at the same time.
        """
        async with self.message_lock:
            self.message_count += 1

    async def update_messages_now(self):
        async with self.message_lock:
            await self.send("messages", str(self.message_count))
            self.message_count = 0

    async def update_messages_loop(self):
        while True:
            await asyncio.sleep(self.message_interval)
            if self.message_count:
                try:
                    await self.update_messages_now()
                except ApiError as e:
                    logger.error(str(e))

    def hook_bot(self, bot):
        """Hook the on_message events of a discord.py bot."""
        bot.add_listener(self.increment_messages, "on_message")
