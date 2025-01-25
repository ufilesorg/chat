import uuid
import asyncio
import itertools

from metisai.async_metis import AsyncMetisBot
from metisai.metistypes import Session
from server.config import Settings
from fastapi_mongo_base.utils import basic
from ufaas import AsyncUFaaS
from ufaas.apps.saas.schemas import UsageCreateSchema

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
async def get_quota(user_id: uuid.UUID):
    ufaas_client = AsyncUFaaS(
        ufaas_base_url=Settings.UFAAS_BASE_URL,
        usso_base_url=Settings.USSO_BASE_URL,
        api_key=Settings.UFILES_API_KEY,
    )
    quotas = await ufaas_client.saas.enrollments.get_quotas(
        user_id=user_id,
        asset="coin",
        variant="chat",
    )
    return quotas.quota

@basic.try_except_wrapper
async def meter_cost(user_id: uuid.UUID, cost: float):
    ufaas_client = AsyncUFaaS(
        ufaas_base_url=Settings.UFAAS_BASE_URL,
        usso_base_url=Settings.USSO_BASE_URL,
        api_key=Settings.UFILES_API_KEY,
    )
    coin_cost = cost * 100
    usage_schema = UsageCreateSchema(
        user_id=user_id,
        asset="coin",
        amount=coin_cost,
        variant="chat",
    )
    usage = await ufaas_client.saas.usages.create_item(
        usage_schema.model_dump(mode="json")
    )
    return usage


@basic.try_except_wrapper
async def register_cost(metis: AsyncMetisBot, session_id: uuid.UUID, user_id: uuid.UUID):
    session = await metis.retrieve_session(session_id)
    if not session.messages:
        return
    cost = session.messages[0].cost
    await meter_cost(user_id, cost)
