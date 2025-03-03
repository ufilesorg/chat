import asyncio
import itertools
import logging
import uuid

from fastapi_mongo_base.utils import basic
from metisai.async_metis import AsyncMetisBot
from metisai.metistypes import Session
from server.config import Settings
from utils import finance, promptly

from . import ai, models


async def get_sessions(engine: ai.AIEngines, user_id: str):
    metis = AsyncMetisBot(api_key=Settings.METIS_API_KEY, bot_id=engine.metis_bot_id)
    return await metis.list_sessions(user_id)


async def get_all_sessions(user_id) -> list[Session]:
    sessions_task = []
    for engine in ai.AIEngines:
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


async def db_session_from_metis_session(
    session: Session | str | uuid.UUID,
) -> models.Session:
    if isinstance(session, str | uuid.UUID):
        session = await AsyncMetisBot(
            api_key=Settings.METIS_API_KEY, bot_id=session
        ).retrieve_session(session)
    user_id = (
        uuid.UUID(session.user.id)
        if isinstance(session.user.id, str)
        else session.user.id
    )
    session_uid = uuid.UUID(session.id) if isinstance(session.id, str) else session.id
    return models.Session(
        uid=session_uid,
        user_id=user_id,
        engine=ai.AIEngines.from_metis_bot_id(session.botId),
    )


async def create_session(engine: ai.AIEngines, user_id: uuid.UUID):
    metis = AsyncMetisBot(api_key=Settings.METIS_API_KEY, bot_id=engine.metis_bot_id)
    session = await metis.create_session(user_id=str(user_id))
    db_session = await db_session_from_metis_session(session)
    await db_session.save()
    return session


@basic.try_except_wrapper
async def set_name(session_id: uuid.UUID, message: str):
    logging.info(f"Setting name for session {session_id}")
    db_session = await models.Session.find_one({"uid": session_id})
    if not db_session:
        logging.info(f"Session {session_id} not found, creating new db session")
        db_session = await db_session_from_metis_session(session_id)

    if db_session.name:
        logging.info(f"Session {session_id} already has a name {db_session.name}")
        return

    async with promptly.PromptlyClient() as client:
        resp = await client.ai(key="session-namer", data={"message": message})

    session_name = resp.get("session_name", "New Session ...")
    language = resp.get("language", None)

    logging.info(
        f"Setting name for session {session_id} to {session_name} and language {language}"
    )

    db_session.name = session_name
    db_session.language = language
    await db_session.save()
    return db_session
