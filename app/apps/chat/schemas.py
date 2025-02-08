import uuid
from datetime import datetime

from fastapi_mongo_base.core.enums import Language
from metisai.metistypes import Message, Session
from pydantic import BaseModel

from . import models
from .ai import AIEngines


class SessionResponse(BaseModel):
    uid: uuid.UUID
    name: str
    created_at: datetime
    engine: AIEngines
    thumbnail_url: str
    price: float
    cost: float
    language: Language = Language.English

    @classmethod
    async def from_session(cls, session: Session, **kwargs):
        engine = AIEngines.from_metis_bot_id(session.botId)

        session_uid = uuid.UUID(session.id) if isinstance(session.id, str) else session.id
        db_session = await models.Session.find_one({"uid": session_uid})
        if not db_session:
            name = "New Session ..."
            language = Language.English
        else:
            name = db_session.name or "New Session ..."
            language = db_session.language or Language.English

        data = {
            "uid": session.id,
            "name": name,
            "language": language,
            "messages": session.messages,
            "created_at": session.startDate,
            "cost": session.cost,
            "engine": engine,
            "thumbnail_url": engine.thumbnail_url,
            "price": engine.price,
        }
        data.update(**kwargs)
        return cls(**data)


class SessionDetailResponse(SessionResponse):
    messages: list[Message]


class PaginatedResponse(BaseModel):
    items: list
    total: int
    offset: int
    limit: int


class AIEnginesSchema(BaseModel):
    engine: AIEngines
    thumbnail_url: str
    price: float

    @classmethod
    def from_model(cls, engine: AIEngines):
        return cls(
            engine=engine,
            thumbnail_url=engine.thumbnail_url,
            price=engine.price,
        )
