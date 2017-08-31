import asyncio
import aiohttp
import logging
import typing

from analyticord import errors

logger = logging.getLogger("analyticord")

base_address = "https://analyticord.solutions"
login_address = base_address + "/api/botLogin"
send_address = base_address + "/api/submit"
get_address = base_address + "/api/getData"
botinfo_address = base_address + "/api/botinfo"
botlist_address = base_address + "/api/botlist"


def _make_error(error, **kwargs) -> errors.ApiError:
    name = error.get("error", "")  # type: str
    name = name[:1].upper() + name[1:]

    err = getattr(errors, name, None)

    if err is None:
        return errors.ApiError(**error, **kwargs)

    return err(**error, **kwargs)


class EventProxy:
    def __init__(self, analytics, anal_name: str):
        """
        Proxy class to make events and actions acessible through dot notation

        :param analytics: The :class:`analyticord.AnalytiCord` this proxy is tied to.
        :param anal_name: The analyticord name of the event.
        """
        self.analytics = analytics
        self.anal_name = anal_name
        self.lock = asyncio.Lock()
        self.counter = 0

    def send(self, count: int):
        """Invoke this events send message."""
        return self.analytics.send(self.anal_name, count)

    def hook_bot(self, dpy_name: str, bot):
        """Hook the event of a discord.py bot to this event.

        :param dpy_name: Name of discord.py event.
        :param bot: An instance of a discord.py :class:`discord.ext.commands.Bot`.
        """
        async def _hook(*_, **__):
            await self.increment()

        bot.add_listener(_hook, dpy_name)

    async def increment(self):
        """Increment this events counter."""
        async with self.lock:
            self.counter += 1

    async def update_now(self):
        "Trigger an update of this event, resetting the counter."
        async with self.lock:
            resp = await self.send(self.counter)
            self.counter = 0
            return resp


class AnalytiCord:
    """Represents an AnalytiCord api object.

    Instantiation example:

    .. code-block:: python3

        analytics = AnalytiCord("token", "user_token")
        await analytics.start()

    """

    #: Default listeners in format (discord event, analyticord event)
    default_listens = ("messages", "guildJoin",)

    def __init__(self,
                 token: str,
                 user_token: str=None,
                 event_interval: int=60,
                 session: aiohttp.ClientSession=None,
                 loop=None):
        """
        :param token: Your AnalytiCord bot token.
        :param user_token:
            Your AnalytiCord user token.
            This is not required unless you wish to use endpoints that require User auth.
        :param event_interval: The interval between sending event updates in seconds.

        """

        #: Your AnalytiCord bot token.
        self.token = "bot {}".format(token)

        self.loop = loop or asyncio.get_event_loop()
        self.session = session or aiohttp.ClientSession()

        #: Interval between sending event updates
        self.event_interval = event_interval

        if user_token is not None:
            self.user_token = "user {}".format(user_token)

        self.events = {i: EventProxy(self, i) for i in self.default_listens}

        self.updater = None  # placeholder for updater event

    def __getattr__(self, attr):
        return self.events[attr]

    @property
    def _auth(self):
        return {"Authorization": self.token}

    @property
    def _user_auth(self):
        if not hasattr(self, "user_token"):
            raise Exception("user_token must be set to use this feature.")
        return {"Authorization": self.user_token}

    def register(self, anal_name: str):
        """Register an event.

        Once registered, AnalytiCord.<anal_name> will return a :class:`analyticord.EventProxy`
        for the given <anal_name>.

        This allows you to do:
        await AnalytiCord.event.increment()  # isend me inncrement the event counter
        AnalytiCord.event.hook_bot(bot)  # hook the event to a bot

        :param anal_name: The AnalytiCord event name, for example: messages, guildJoin.
        """
        self.events[anal_name] = EventProxy(self, anal_name)

    async def _do_request(self, rtype: str, endpoint: str, auth, **kwargs):
        req = getattr(self.session, rtype)
        async with req(endpoint, headers=auth, **kwargs) as resp:
            body = await resp.json()
            if resp.status != 200:
                raise _make_error(body, status=resp.status)
            return body

    async def start(self):
        """Fire a login event.
        Also runs the event updater loop

        :raises: :class:`analyticord.errors.ApiError`.
        """
        resp = await self._do_request("get", login_address, self._auth)
        self.updater = self.loop.create_task(self._update_events_loop())
        return resp

    async def stop(self):
        """Update all events and stop the analyticord updater loop."""
        self.updater.cancel()
        await self._update_once()

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

    async def _update_once(self):
        for event in self.events.values():
            if event.counter:
                try:
                    await event.update_now()
                except errors.ApiError as e:
                    logger.error(str(e))

    async def _update_events_loop(self):
        while True:
            await asyncio.sleep(self.event_interval)
            await self._update_once()
