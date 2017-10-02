import asyncio
import os

import pytest

from analyticord import AnalytiCord

bot_token = os.environ["ANALYTICORD_BOT"]
user_token = os.environ["ANALYTICORD_USER"]


@pytest.fixture(scope="module")
async def analytics() -> AnalytiCord:
    return AnalytiCord(bot_token, user_token)


@pytest.fixture(scope="module")
def event_loop():
    return asyncio.get_event_loop()
