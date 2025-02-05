import asyncio
import logging
import uuid
from datetime import datetime

import fastapi
from aiocache import cached
from fastapi import Body, Query
from fastapi.responses import StreamingResponse
from fastapi_mongo_base.routes import AbstractBaseRouter
from metisai.async_metis import AsyncMetisBot
from metisai.metistypes import Session
from server.config import Settings
from usso.fastapi import jwt_access_security
from utils import finance

from . import ai, services
from .schemas import (
    AIEnginesSchema,
    PaginatedResponse,
    SessionDetailResponse,
    SessionResponse,
)


class SessionRouter(AbstractBaseRouter[Session, SessionResponse]):
    def __init__(self):
        super().__init__(
            model=Session,
            schema=SessionResponse,
            user_dependency=jwt_access_security,
            tags=["Chat"],
            prefix="",
        )
        self.metis = AsyncMetisBot(api_key=Settings.METIS_API_KEY)

    def config_schemas(self, schema, **kwargs):
        super().config_schemas(schema, **kwargs)
        self.list_response_schema = PaginatedResponse
        self.retrieve_response_schema = SessionDetailResponse

    def config_routes(self, **kwargs):
        super().config_routes(prefix="/sessions", update_route=False)
        self.router.add_api_route(
            "/sessions/{uid:uuid}/messages",
            self.chat_messages,
            methods=["POST"],
            status_code=200,
        )
        self.router.add_api_route(
            "/sessions/{uid:uuid}/messages/{mid:uuid}",
            self.chat_messages_async,
            methods=["GET"],
            status_code=200,
        )

    @cached(ttl=60 * 60 * 24)
    async def get_item(self, uid: uuid.UUID, **kwargs):
        return await self.metis.retrieve_session(session_id=uid)

    async def retrieve_item(self, request: fastapi.Request, uid: uuid.UUID):
        user_id = await self.get_user_id(request)
        session = await self.get_item(uid, user_id=user_id, time=datetime.now())
        return await SessionDetailResponse.from_session(session)

    async def list_items(
        self,
        request: fastapi.Request,
        offset: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=Settings.page_max_limit),
    ):
        user_id = await self.get_user_id(request)
        # sessions = await get_all_sessions_sorted(user_id)
        sessions = await self.metis.list_sessions(user_id)
        sessions = [await SessionResponse.from_session(session) for session in sessions]
        # TODO request paginated sessions
        return PaginatedResponse(
            items=sessions[offset : offset + limit],
            total=len(sessions),
            offset=offset,
            limit=limit,
        )

    async def create_item(
        self,
        request: fastapi.Request,
        engine: ai.AIEngines = Body(ai.AIEngines.gpt_4o, embed=True),
    ):
        user_id = await self.get_user_id(request)
        session = await services.create_session(engine, user_id)
        return await SessionResponse.from_session(session)

    async def delete_item(self, request: fastapi.Request, uid: uuid.UUID):
        await self.get_user_id(request)
        res = await self.metis.delete_session(session=uid)
        return res

    async def chat_messages(
        self,
        request: fastapi.Request,
        uid: uuid.UUID,
        message: str = Body(embed=True),
        async_task: bool = False,
        stream: bool = False,
        # split_criteria: dict = None,
    ):
        user_id = await self.get_user_id(request)
        quota = await finance.check_quota(
            user_id, len(message) * ai.AIEngines.gpt_4o.input_token_price / 1000
        )

        asyncio.create_task(services.set_name(uid, message))

        if stream:
            response = self.metis.stream_messages(
                session=uid, prompt=message, split_criteria={}
            )

            async def generate():
                async for msg in response:
                    logging.info(msg.message.content)
                    yield msg.message.content + "\n"

                asyncio.create_task(services.register_cost(self.metis, uid, user_id))

            return StreamingResponse(generate(), media_type="text/plain")
        if async_task:
            return await self.metis.send_message_async(session=uid, prompt=message)
        return await self.metis.send_message(session=uid, prompt=message)

    async def chat_messages_async(
        self, request: fastapi.Request, uid: uuid.UUID, mid: uuid.UUID
    ):
        _ = await self.get_user_id(request)
        return await self.metis.retrieve_async_task(session=uid, task_id=mid)


router = SessionRouter().router


@router.get("/engines")
async def chat_engines():
    engines = [AIEnginesSchema.from_model(engine) for engine in ai.AIEngines]
    return engines
