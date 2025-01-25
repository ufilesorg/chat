import asyncio
import itertools

from metisai.async_metis import AsyncMetisBot
from server.config import Settings

from .models import AIEngines


async def get_sessions(engine: AIEngines, user_id: str):
    metis = AsyncMetisBot(api_key=Settings.METIS_API_KEY, bot_id=engine.metis_bot_id)
    return await metis.list_sessions(user_id)


async def get_all_sessions(user_id):
    sessions_task = []
    for engine in AIEngines:
        sessions_task.append(get_sessions(engine, user_id))

    sessions2d = await asyncio.gather(*sessions_task)
    return list(itertools.chain.from_iterable(sessions2d))


async def get_all_sessions_sorted(user_id):
    sessions = await get_all_sessions(user_id)
    return sorted(sessions, key=lambda session: session.startDate, reverse=True)
