import asyncio
import json
import logging
import uuid
from datetime import datetime

import fastapi
from aiocache import cached
from fastapi import Body, Query, WebSocket
from fastapi.responses import StreamingResponse
from fastapi_mongo_base.routes import AbstractBaseRouter
from metisai.async_metis import AsyncMetisBot
from metisai.metistypes import Session
from server.config import Settings
from usso.fastapi import jwt_access_security
from utils import finance

from . import ai, models, services
from .schemas import (
    AIEnginesSchema,
    PaginatedResponse,
    SessionDetailResponse,
    SessionResponse,
    SessionUpdateRequest,
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
        # self.connection_manager = ConnectionManager()

    def config_schemas(self, schema, **kwargs):
        super().config_schemas(schema, **kwargs)
        self.list_response_schema = PaginatedResponse
        self.retrieve_response_schema = SessionDetailResponse

    def config_routes(self, **kwargs):
        super().config_routes(prefix="/sessions")
        self.router.add_api_route(
            "/sessions/messages",
            self.create_session_chat_messages,
            methods=["POST"],
            status_code=200,
        )
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
        # self.router.add_api_route(
        #     "/sessions/{uid:uuid}/ws",
        #     self.websocket_endpoint,
        #     methods=["GET"],
        # )
        self.router.add_websocket_route(
            "/sessions/ws/stream",
            self.websocket_stream_endpoint,
        )
        self.router.add_websocket_route(
            "/sessions/ws/stream2",
            self.websocket1,
        )
        self.router.add_websocket_route(
            "/sessions/ws/stream3",
            self.websocket2,
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
        try:
            user_id = await self.get_user_id(request)
            session = await services.create_session(engine, user_id)
            return await SessionResponse.from_session(session)
        except Exception as e:
            logging.error(f"Error creating session: {e}")
            raise fastapi.HTTPException(status_code=500, detail=str(e))

    async def update_item(
        self,
        request: fastapi.Request,
        uid: uuid.UUID,
        data: SessionUpdateRequest,
    ):
        user_id = await self.get_user_id(request)
        model_session: models.Session = await models.Session.get_item(
            uid, user_id=user_id
        )
        model_session.name = data.name
        await model_session.save()
        session = await self.get_item(uid, user_id=user_id)
        return await SessionDetailResponse.from_session(session)

        try:
            user_id = await self.get_user_id(request)
            session = await services.create_session(engine, user_id)
            return await SessionResponse.from_session(session)
        except Exception as e:
            logging.error(f"Error creating session: {e}")
            raise fastapi.HTTPException(status_code=500, detail=str(e))

    async def delete_item(self, request: fastapi.Request, uid: uuid.UUID):
        await self.get_user_id(request)
        res = await self.metis.delete_session(session=uid)
        return res

    async def create_session_chat_messages(
        self,
        request: fastapi.Request,
        message: str = Body(embed=True),
        async_task: bool = False,
        stream: bool = False,
        engine: ai.AIEngines = Body(ai.AIEngines.gpt_4o, embed=True),
        # split_criteria: dict = None,
    ):
        user_id = await self.get_user_id(request)
        quota = await finance.check_quota(
            user_id, len(message) * engine.input_token_price / 1000
        )

        session = await services.create_session(engine, user_id)
        uid = uuid.UUID(session.id) if isinstance(session.id, str) else session.id

        asyncio.create_task(services.set_name(uid, message))

        if stream:
            response = self.metis.stream_messages(
                session=uid, prompt=message, split_criteria={}
            )

            async def generate():
                try:
                    import json

                    # Send an initial empty data event to establish the connection
                    yield "data: {}\n\n"

                    # Send session UID as the first message
                    data = json.dumps({"uid": str(uid)}, ensure_ascii=False)
                    yield f"data: {data}\n\n"

                    async for msg in response:
                        chunk = msg.message.content
                        # logging.info(chunk)
                        # Properly format as SSE with JSON data
                        data = json.dumps({"message": chunk}, ensure_ascii=False)
                        yield f"data: {data}\n\n"
                        # Force each chunk to be sent immediately
                        await asyncio.sleep(0)
                except Exception as e:
                    logging.error(f"Error during message streaming: {e}")
                    error_data = json.dumps({"error": str(e)}, ensure_ascii=False)
                    yield f"data: {error_data}\n\n"
                finally:
                    asyncio.create_task(
                        services.register_cost(self.metis, uid, user_id)
                    )

            return StreamingResponse(
                generate(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",  # Disable Nginx buffering if you're using Nginx
                    "Content-Type": "text/event-stream",
                },
            )
        if async_task:
            return (
                await self.metis.send_message_async(session=uid, prompt=message)
            ).model_dump() | {"uid": uid}
        response = await self.metis.send_message(session=uid, prompt=message)
        return response.model_dump() | {"uid": uid}

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
                try:
                    import json

                    # Send an initial empty data event to establish the connection
                    yield "data: {}\n\n"

                    # Send session UID as the first message
                    data = json.dumps({"uid": str(uid)}, ensure_ascii=False)
                    yield f"data: {data}\n\n"

                    async for msg in response:
                        chunk = msg.message.content
                        # logging.info(chunk)
                        # Properly format as SSE with JSON data
                        data = json.dumps({"message": chunk}, ensure_ascii=False)
                        yield f"data: {data}\n\n"
                        # Force each chunk to be sent immediately
                        await asyncio.sleep(0)
                except Exception as e:
                    logging.error(f"Error during message streaming: {e}")
                    error_data = json.dumps({"error": str(e)}, ensure_ascii=False)
                    yield f"data: {error_data}\n\n"
                finally:
                    asyncio.create_task(
                        services.register_cost(self.metis, uid, user_id)
                    )

            return StreamingResponse(
                generate(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",  # Disable Nginx buffering if you're using Nginx
                    "Content-Type": "text/event-stream",
                },
            )
        if async_task:
            return await self.metis.send_message_async(session=uid, prompt=message)
        return await self.metis.send_message(session=uid, prompt=message)

    async def chat_messages_async(
        self, request: fastapi.Request, uid: uuid.UUID, mid: uuid.UUID
    ):
        _ = await self.get_user_id(request)
        return await self.metis.retrieve_async_task(session=uid, task_id=mid)

    # @basic.try_except_wrapper
    async def websocket_stream_endpoint(
        self,
        websocket: WebSocket,
        # uid: uuid.UUID | None = None,
        # engine: ai.AIEngines = ai.AIEngines.gpt_4o,
    ):
        try:
            await websocket.accept()

            # Check authentication
            token = websocket.cookies.get("usso_access_token")
            if not token:
                logging.error("Missing authentication token")
                await websocket.close(code=1008, reason="Missing authentication token")
                return

            try:
                user_id = await self.get_user_id(websocket)
                logging.info(f"Authenticated user: {user_id}")
            except Exception as e:
                logging.error(f"Authentication error: {e}")
                await websocket.close(code=1008, reason="Authentication failed")
                return

            message = await websocket.receive_text()
            quota = await finance.check_quota(
                user_id, len(message) * engine.input_token_price / 1000
            )

            logging.info(f"Message: {message}")

            uid = websocket.query_params.get("uid")
            engine = websocket.query_params.get("engine")

            if uid is None:
                session = await services.create_session(engine, user_id)
                uid = (
                    uuid.UUID(session.id) if isinstance(session.id, str) else session.id
                )
                await websocket.send_json({"uid": str(uid)})

            try:
                response = self.metis.stream_messages(
                    session=uid, prompt=message, split_criteria={}
                )
                async for msg in response:
                    chunk = msg.message.content
                    data = json.dumps({"message": chunk}, ensure_ascii=False)
                    await websocket.send_text(data)
            except Exception as e:
                logging.error(f"Error during message streaming: {e}")
                error_data = json.dumps({"error": str(e)}, ensure_ascii=False)
                await websocket.send_text(error_data)
            finally:
                asyncio.create_task(services.register_cost(self.metis, uid, user_id))
                await websocket.close()

        except Exception as e:
            logging.error(f"WebSocket connection error: {e}")
            try:
                await websocket.close(code=1011, reason=f"Server error")
            except:
                pass
            # raise

    async def websocket1(self, websocket: WebSocket):    
        try:
            import openai
            client = openai.OpenAI(api_key=Settings.METIS_API_KEY, base_url="https://api.metisai.ir/openai/v1")
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "Hello, world!"}],
                stream=True,
            )
            async for chunk in response:
                await websocket.send_text(chunk)

        except Exception as e:
            logging.error(f"WebSocket connection error: {e}")
            try:
                await websocket.close(code=1011, reason=f"Server error")
            except:
                pass
            # raise

    async def websocket2(self, websocket: WebSocket):
        try:
            for chunk in range(20):
                sample_text = f"Hello, world! {chunk}"
                await websocket.send_text(sample_text)
                await asyncio.sleep(1)

        except Exception as e:
            logging.error(f"WebSocket connection error: {e}")
            try:
                await websocket.close(code=1011, reason=f"Server error")
            except:
                pass
            # raise


router = SessionRouter().router


@router.get("/engines")
async def chat_engines():
    engines = [AIEnginesSchema.from_model(engine) for engine in ai.AIEngines]
    return engines
