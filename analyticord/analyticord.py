import asyncio
import aiohttp
import logging

from analyticord import errors

logger = logging.getLogger("analyticord")

base_address = "https://api.analyticord.solutions"
login_address = base_address + "/api/botLogin"
send_address = base_address + "/api/submit"
get_address = base_address + "/api/getData"
botinfo_address = base_address + "/api/botinfo"
botlist_address = base_address + "/api/botlist"


def _make_error(error, **kwargs) -> errors.ApiError:
    name = error.get("name", "")  # type: str
    name = name[:1].lower() + name[1:]

    err = getattr(errors, name, None)

    if err is None:
        return errors.ApiError(**error, **kwargs)

    return err(**error, **kwargs)


class AnalytiCord:
    """Represents an AnalytiCord api object.

    Instantiation example:

    .. code-block:: python3

        analytics = AnalytiCord("token", "user_token")
        await analytics.start()

    """

    def __init__(self,
                 token: str,
                 user_token: str=None,
                 message_interval: int=60,
                 session: aiohttp.ClientSession=None,
                 loop=None):
        """
        :param token: Your AnalytiCord bot token.
        :param user_token:
            Your AnalytiCord user token.
            This is not required unless you wish to use endpoints that require User auth.
        :param message_interval: The interval between sending message updates in seconds.

        """

        #: Yout AnalytiCord bot token.
        self.token = "bot {}".format(token)

        self.loop = loop or asyncio.get_event_loop()
        self.session = session or aiohttp.ClientSession()

        #: Interval between sending message count updates in seconds.
        self.message_interval = message_interval

        if user_token is not None:
            self.user_token = "user {}".format(user_token)

        self.message_lock = asyncio.Lock()

        #: The message counter.
        self.message_count = 0

    @property
    def _auth(self):
        return {"Authorization": self.token}

    @property
    def _user_auth(self):
        if not hasattr(self, "user_token"):
            raise Exception("user_token must be set to use this feature.")
        return {"Authorization": self.user_token}

    async def __do_request(self, rtype: str, endpoint: str, auth, **kwargs):
        req = getattr(self.session, rtype)
        async with req(endpoint, headers=auth, **kwargs) as resp:
            body = await resp.json()
            if resp.status != 200:
                raise _make_error(body, status=resp.status)
            return body

    async def start(self):
        """Start up analyticord connection.
        Also runs the message updater loop

        :raises: :class:`analyticord.errors.ApiError`.
        """
        await self._do_request("get", login_address, self._auth)

        self.loop.create_task(self.update_messages_loop())

    async def send(self, event_type: str, data: str) -> dict:
        """Send data to analiticord.

        :param event_type: Event type to send.
        :param data: Data to send.

        :return: Dict response from api.

        :raises: :class:`analyticord.errors.ApiError`.
        """
        return await self._do_request("post", send_address, self._auth,
                                      data=dict(eventType=event_type, data=data))

    async def get(self, **attrs) -> list:
        """Get data from the api.

        :param attrs: Kwarg attributes passed to get request params.

        :return: Response list on success.

        :raises:  :class:`analyticord.errors.ApiError`.
        """
        return await self._do_request("get", get_address, self._user_auth, params=attrs)

    async def bot_info(self, id: int) -> dict:
        """Get info for a bot id.

        :param id: The ID of the bot to get info for.

        :return: Bot info data.

        :raises: :class:`analyticord.errors.ApiError`.
        """
        return await self._do_request("get", botinfo_address, self._user_auth,
                                      params={"id": id})

    async def bot_list(self) -> list:
        """Get list of bots owned by this auth.

        :return: list of bot info data.

        :raises: :class:`analyticord.errors.ApiError`.
        """
        return await self._do_request("get", botlist_address, self._user_auth)

    async def increment_messages(self):
        """Increment the message count.

        Asynchronous because we wait for a lock on incrementing the message count.
        """
        async with self.message_lock:
            self.message_count += 1

    async def update_messages_now(self):
        """Trigger sending of a message update event, also resets the counter."""
        async with self.message_lock:
            resp = await self.send("messages", self.message_count)
            self.message_count = 0
            return resp

    async def _update_messages_loop(self):
        while True:
            await asyncio.sleep(self.message_interval)
            if self.message_count:
                try:
                    await self.update_messages_now()
                except errors.ApiError as e:
                    logger.error(str(e))

    def hook_bot(self, bot):
        """Hook the on_message events of a discord.py bot.
        Such that receiveing messages increments the counter.

        :param bot: An instance of a discord.py :class:`discord.ext.commands.Bot`.
        """
        async def _hook(message):
            await self.increment_messages()

        bot.add_listener(_hook, "on_message")
