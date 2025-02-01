import asyncio
import itertools
import uuid

from fastapi_mongo_base.utils import basic
from metisai.async_metis import AsyncMetisBot
from metisai.metistypes import Session
from server.config import Settings
from utils import finance

from .models import AIEngines


async def get_sessions(engine: AIEngines, user_id: str):
    metis = AsyncMetisBot(api_key=Settings.METIS_API_KEY, bot_id=engine.metis_bot_id)
    return await metis.list_sessions(user_id)


async def get_all_sessions(user_id) -> list[Session]:
    sessions_task = []
    for engine in AIEngines:
        sessions_task.append(get_sessions(engine, user_id))

    sessions2d = await asyncio.gather(*sessions_task)
    return list(itertools.chain.from_iterable(sessions2d))


async def get_all_sessions_sorted(user_id):
    sessions = await get_all_sessions(user_id)
    return sorted(sessions, key=lambda session: session.startDate, reverse=True)


@basic.try_except_wrapper
async def register_cost(
    metis: AsyncMetisBot, session_id: uuid.UUID, user_id: uuid.UUID
):
    session = await metis.retrieve_session(session_id)
    if not session.messages:
        return
    cost = session.messages[0].cost
    await finance.meter_cost(user_id, cost)
