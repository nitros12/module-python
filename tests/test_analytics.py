import pytest

from analyticord import AnalytiCord
from analyticord.errors import WrongToken

pytestmark = pytest.mark.asyncio


async def test_start(analytics: AnalytiCord):
    resp = await analytics.start()
    assert "name" in resp
    assert "id" in resp
    assert "owner" in resp


async def test_send(analytics: AnalytiCord):
    resp = await analytics.messages.send(69)
    assert "status" in resp
    assert "ID" in resp


async def test_send_message_update(analytics: AnalytiCord):
    await analytics.messages.increment()
    await analytics.messages.increment()
    resp = await analytics.messages.update_now()
    assert "status" in resp
    assert "ID" in resp


async def test_register(analytics: AnalytiCord):
    class DummyBot:
        def __init__(self):
            self.events = {}

        def add_listener(self, callback, name):
            self.events[name] = callback

    bot = DummyBot()
    analytics.messages.hook_bot(bot)
    assert "on_message" in bot.events


async def test_fail():
    try:
        t = AnalytiCord("fail_token")
        await t.start()
    except WrongToken:
        pass


async def test_stop(analytics: AnalytiCord):
    await analytics.stop()
