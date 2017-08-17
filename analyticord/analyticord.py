import asyncio
import aiohttp
import logging
import typing
import functools

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

    base_address = "http://api.analyticord.solutions:5000"
    login_address = base_address + "/api/botLogin"
    send_address = base_address + "/api/submit"
    get_address = base_address + "/api/getData"
    botinfo_address = base_address + "/api/botinfo"
    botlist_address = base_address + "/api/botlist"

    def __init__(self,
                 token: str,
                 user_token: str=None,
                 message_interval: int=60,
                 session: aiohttp.ClientSession=None,
                 loop=None):
        self.token = f"bot {token}"
        self.loop = asyncio.get_event_loop() if loop is None else loop
        self.session = aiohttp.ClientSession() if session is None else session
        self.message_interval = message_interval

        if user_token is not None:
            self.user_token = f"user {user_token}"

        self.message_lock = asyncio.Lock()
        self.message_count = 0

    @property
    def auth(self):
        return {"Authorization": self.token}

    @property
    def user_auth(self):
        if not hasattr(self, "user_token"):
            raise Exception("user_token must be set to use this feature.")
        return {"Authorization": self.user_token}

    async def do_request(self, rtype: str, endpoint: str, auth, **kwargs):
        req = getattr(self.sessiong, rtype)
        async with req(endpoint, headers=auth, **kwargs) as resp:
            body = await resp.json()
            if resp.status != 200:
                raise ApiError(status=resp.status, **body)
            return body

    async def start(self):
        """Start up analyticord connection.
        Also runs the message updater loop

        :raises: :class:`analyticord.ApiError` on error.
        """
        await self.do_request("get", AnalytiCord.login_address, self.auth)

        self.loop.create_task(self.update_messages_loop())

    async def send(self, event_type: str, data: str) -> dict:
        """Send data to analiticord.

        :param event_type: Event type to send.
        :param data: Data to send.

        :return: Dict response from api.

        :raises: :class:`analyticord.ApiError` on error.
        """
        return await self.do_request("post", AnalytiCord.send_address, self.auth,
                                     data=dict(eventType=event_type, data=data))

    async def get(self, **attrs) -> list:
        """Get data from the api.

        :param attrs: Kwarg attributes passed to get request params.

        :return: Response list on success.

        :raises:  :class:`analyticord.ApiError` on error.
        """
        return await self.do_request("get", AnalytiCord.get_address, self.user_auth, params=attrs)

    async def bot_info(self, id: int) -> dict:
        """Get info for a bot id.

        :param id: The ID of the bot to get info for.

        :return: Bot info data.

        :raises: :class:`analyticord.ApiError` on error.
        """
        return await self.do_request("get", AnalytiCord.botinfo_address, self.user_auth,
                                     params={"id": id})

    async def bot_list(self) -> list:
        """Get list of bots owned by this auth.

        :return: list of bot info data.

        :raises: :class:`analyticord.ApiError` on error.
        """
        return await self.do_request("get", AnalytiCord.botlist_address, self.user_auth)

    async def increment_messages(self, *_):
        """Increment the message count.

        This blocks if a message update is occuring at the same time.
        """
        async with self.message_lock:
            self.message_count += 1

    async def update_messages_now(self):
        async with self.message_lock:
            resp = await self.send("messages", self.message_count)
            self.message_count = 0
            return resp

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
