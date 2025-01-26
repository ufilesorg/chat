import uuid
from datetime import datetime

from metisai.metistypes import Message, Session
from pydantic import BaseModel

from .models import AIEngines


class SessionResponse(BaseModel):
    uid: uuid.UUID
    name: str
    created_at: datetime

    @classmethod
    def from_session(cls, session: Session):
        from fastapi_mongo_base.utils import texttools

        engine = AIEngines.from_metis_bot_id(session.botId)
        initial_text = texttools.sanitize_filename(
            session.messages[0].content or "" if session.messages else "", 60
        )
        return cls(
            uid=session.id,
            name=initial_text,
            messages=session.messages,
            created_at=session.startDate,
            cost=session.cost,
            engine=engine,
            thumbnail_url=engine.thumbnail_url,
            price=engine.price,
        )


class SessionDetailResponse(SessionResponse):
    messages: list[Message]
    cost: float
    engine: AIEngines
    thumbnail_url: str
    price: float


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
