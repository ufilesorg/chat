import logging
import uuid

import fastapi
from fastapi import Body, Query
from fastapi.responses import StreamingResponse
from fastapi_mongo_base.routes import AbstractBaseRouter
from metisai.async_metis import AsyncMetisBot
from metisai.metistypes import Session
from server.config import Settings
from usso.fastapi import jwt_access_security

from .models import AIEngines
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
        self.metis = AsyncMetisBot(
            api_key=Settings.METIS_API_KEY
        )

    def config_schemas(self, schema, **kwargs):
        super().config_schemas(schema, **kwargs)
        self.list_response_schema = PaginatedResponse
        self.retrieve_response_schema = SessionDetailResponse

    def config_routes(self, **kwargs):
        self.router.add_api_route(
            "/sessions/",
            self.list_items,
            methods=["GET"],
            response_model=self.list_response_schema,
            status_code=200,
        )
        self.router.add_api_route(
            "/sessions/{uid:uuid}",
            self.retrieve_item,
            methods=["GET"],
            response_model=self.retrieve_response_schema,
            status_code=200,
        )
        self.router.add_api_route(
            "/sessions/",
            self.create_item,
            methods=["POST"],
            response_model=self.create_response_schema,
            status_code=201,
        )
        self.router.add_api_route(
            "/sessions/{uid:uuid}",
            self.delete_item,
            methods=["DELETE"],
            status_code=204,
        )

    async def get_item(self, uid: uuid.UUID, **kwargs):
        return await self.metis.retrieve_session(session_id=uid)

    async def retrieve_item(self, request: fastapi.Request, uid: uuid.UUID):
        session = await super().retrieve_item(request, uid)
        return SessionDetailResponse.from_session(session)

    async def list_items(
        self,
        request: fastapi.Request,
        offset: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=Settings.page_max_limit),
    ):
        user_id = await self.get_user_id(request)
        # sessions = await get_all_sessions_sorted(user_id)
        sessions = await self.metis.list_sessions(user_id)
        sessions = [SessionResponse.from_session(session) for session in sessions]
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
        engine: AIEngines = Body(AIEngines.gpt_4o, embed=True),
    ):
        user_id = str(await self.get_user_id(request))
        session = await self.metis.create_session(user_id=user_id, bot_id=engine.metis_bot_id)
        return SessionResponse.from_session(session)

    async def delete_item(self, request: fastapi.Request, uid: uuid.UUID):
        await self.get_user_id(request)
        res = await self.metis.delete_session(session=uid)
        return res


router = SessionRouter().router
metis = SessionRouter().metis


@router.post("/sessions/{uid:uuid}/messages")
async def chat_messages(
    uid: uuid.UUID,
    message: str = Body(embed=True),
    async_task: bool = False,
    stream: bool = False,
    # split_criteria: dict = None,
):
    if stream:
        response = metis.stream_messages(session=uid, prompt=message, split_criteria={})

        async def generate():
            async for msg in response:
                logging.info(msg.message.content)
                yield msg.message.content + "\n"

        return StreamingResponse(generate(), media_type="text/plain")
    if async_task:
        return await metis.send_message_async(session=uid, prompt=message)
    return await metis.send_message(session=uid, prompt=message)


@router.get("/sessions/{uid:uuid}/messages/{mid:uuid}")
async def chat_messages_async(uid: uuid.UUID, mid: uuid.UUID):
    return await metis.retrieve_async_task(session=uid, task_id=mid)


@router.get("/engines")
async def chat_engines():
    engines = [AIEnginesSchema.from_model(engine) for engine in AIEngines]
    return engines
