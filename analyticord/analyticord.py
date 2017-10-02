import asyncio
import logging
import typing

import aiohttp

from analyticord import errors

logger = logging.getLogger("analyticord")


def route(*ends) -> str:
    """Formats into a route.

    route("api", "botLogin") -> "https://analyticord.solutions/api/botLogin
    """
    s = "https://analyticord.solutions"
    return "/".join((s, *ends))


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

        :param analytics: The :class:`AnalytiCord` this proxy is tied to.
        :param anal_name: The analyticord name of the event.
        """
        self.analytics = analytics
        self.anal_name = anal_name

    def __str__(self):
        return "Analyticord event: {}".format(self.__class__.__name__)

    def send(self, value: typing.Any):
        """Invoke this events send message."""
        return self.analytics.send(self.anal_name, value)

    def hook_bot(self, bot, dpy_name: str):
        """Hook a discord event to commiting the relevent action for this event.

        :param dpy_name: name of discord.py event.
        :param bot: an instance of a discord.py :class:`discord.ext.commands.bot`.
        """

        async def _hook(*_, **__):
            await self.send(True)

        bot.add_listener(_hook, dpy_name)


class MessageEventProxy(EventProxy):
    """Basically, only message event takes a delta value.
    Everything else is exact, so half the stuff in EventProxy is useless for anything but `messages`
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lock = asyncio.Lock()
        self.counter = 0

    def __str__(self):
        return "{}, counting {} messages".format(super().__str__(), self.counter)

    def hook_bot(self, bot, dpy_name: str="on_message"):
        """Hook a discord event to increment the message count.

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
        """Trigger an update of this event, resetting the counter."""
        async with self.lock:
            resp = await self.send(self.counter)
            self.counter = 0
            return resp

    async def _update_once(self):
        if self.counter:
            try:
                await self.update_now()
            except errors.ApiError as e:
                logger.error(str(e))

    async def _update_events_loop(self):
        while True:
            await asyncio.sleep(self.analytics.event_interval)
            await self._update_once()


class ErrorEventProxy(EventProxy):
    """Proxy class for the error event."""

    def hook_bot(self, bot, dpy_name: str="on_command_error"):
        """Hook a discord event to send an error event.

        :param dpy_name: name of discord.py event.
        :param bot: an instance of a discord.py :class:`discord.ext.commands.bot`.
        """

        async def _hook(ctx, exception):
            await self.send("command: {}. error: {}.".format(ctx, exception))

        bot.add_listener(_hook, dpy_name)


class GuildJoinEventProxy(EventProxy):
    """Proxy class for the guild join event."""

    def hook_bot(self, bot, dpy_name: str="on_guild_join"):
        """Hook a discord event to send a guildJoin event.

        :param dpy_name: name of discord.py event.
        :param bot: an instance of a discord.py :class:`discord.ext.commands.bot`.
        """

        async def _hook(*_, **__):
            await self.send(len(bot.guilds))

        bot.add_listener(_hook, dpy_name)


class CommandUsedEventProxy(EventProxy):
    """Proxy used for the command used event."""

    def hook_bot(self, bot, dpy_name: str="on_command_completion"):
        """Hook a discord event to send a commandUsed event.

        :param dpy_name: name of discord.py event.
        :param bot: an instance of a discord.py :class:`discord.ext.commands.bot`.
        """

        async def _hook(ctx):
            await self.send(ctx.command.name)

        bot.add_listener(_hook, dpy_name)


class AnalytiCord:
    """Represents an AnalytiCord api object.

    Example:

    .. code-block:: python3

        analytics = AnalytiCord("token", "user_token")
        await analytics.start()

        analytics.messages.hook_bot(bot)
        analytics.guildLeave.hook_bot(bot)

    Default listeners:
    These are the mappings of events that are added to the AnalytiCord instance by default
    And the event proxies they map to.

    ================= ================================
    Event Name        Event Class
    ================= ================================
    messages          :class:`MessageEventProxy`
    guildJoin         :class:`GuildJoinEventProxy`
    error             :class:`ErrorEventProxy`
    guildLeave        :class:`EventProxy`
    disconnect        :class:`EventProxy`
    voiceChannelJoin  :class:`EventProxy`
    guildDetails      :class:`EventProxy`
    mentions          :class:`EventProxy`
    commands_used     :class:`CommandUsedEventProxy`
    ================= ================================

    """

    _default_listens = (("messages", MessageEventProxy),
                        ("guildJoin", GuildJoinEventProxy),
                        ("error", ErrorEventProxy),
                        ("guildLeave", EventProxy),
                        ("disconnect", EventProxy),
                        ("voiceChannelJoin", EventProxy),
                        ("guildDetails", EventProxy),
                        ("mentions", EventProxy),
                        ("commands_used", CommandUsedEventProxy))

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

        #: Number of events sent
        self.sent_events = 0

        self.loop = loop or asyncio.get_event_loop()
        self.session = session or aiohttp.ClientSession()

        #: Interval between sending event updates
        self.event_interval = event_interval

        if user_token is not None:
            self.user_token = "user {}".format(user_token)

        self.events = {i: e(self, i) for i, e in self._default_listens}

        self.updater = None

    def __getattr__(self, attr):
        return self.events[attr]

    def __str__(self):
        return "Analyticord instance. Fired {} events".format(self.sent_events)

    @property
    def _auth(self):
        return {"Authorization": self.token}

    @property
    def _user_auth(self):
        if not hasattr(self, "user_token"):
            raise Exception("user_token must be set to use this feature.")
        return {"Authorization": self.user_token}

    def register(self, anal_name: str, proxy_type: EventProxy=EventProxy):
        """Register an event.

        Once registered, AnalytiCord.<anal_name> will return a :class:`EventProxy`
        for the given <anal_name>.

        This allows you to do:
        :class:`AnalytiCord`.event.send(data)
        :class:`AnalytiCord`.event.hook_bot(bot)  # hook the event to a bot

        :param anal_name: The AnalytiCord event name, for example: messages, guildJoin.
        :param proxy_type: The event proxy to use. Should be a subclass of :class:`EventProxy`.
        """
        self.events[anal_name] = proxy_type(self, anal_name)

    async def _do_request(self, rtype: str, endpoint: str, auth, **kwargs):
        async with self.session.request(
                rtype, endpoint, headers=auth, **kwargs) as resp:
            body = await resp.json()
            if resp.status != 200:
                raise _make_error(body, status=resp.status)
            return body

    async def start(self):
        """Fire a login event.
        Also runs the event updater loop

        :raises: :class:`analyticord.errors.ApiError`.
        """
        resp = await self._do_request("get",
                                      route("api", "botLogin"), self._auth)
        self.updater = self.loop.create_task(
            self.messages._update_events_loop())
        self.sent_events = 0
        return resp

    async def stop(self):
        """Update all events and stop the analyticord updater loop."""
        self.updater.cancel()
        await self.messages._update_once()

    async def send(self, event_type: str, data: str) -> dict:
        """Send data to analyticord.

        :param event_type: Event type to send.
        :param data: Data to send.
        :return: Dict response from api.
        :raises: :class:`analyticord.errors.ApiError`.
        """
        self.sent_events += 1
        return await self._do_request(
            "post",
            route("api", "submit"),
            self._auth,
            data=dict(eventType=event_type, data=data))

    async def get(self, **attrs) -> list:
        """Get data from the api.

        :param attrs: Kwarg attributes passed to get request params.
        :return: Response list on success.
        :raises:  :class:`analyticord.errors.ApiError`.
        """
        return await self._do_request(
            "get", route("api", "getData"), self._user_auth, params=attrs)

    async def bot_info(self, id: int) -> dict:
        """Get info for a bot id.

        :param id: The ID of the bot to get info for.
        :return: Bot info data.
        :raises: :class:`analyticord.errors.ApiError`.
        """
        return await self._do_request(
            "get", route("api", "botinfo"), self._user_auth, params={"id": id})

    async def bot_list(self) -> list:
        """Get list of bots owned by this auth.

        :return: list of bot info data.
        :raises: :class:`analyticord.errors.ApiError`.
        """
        return await self._do_request("get",
                                      route("api", "botlist"), self._user_auth)
