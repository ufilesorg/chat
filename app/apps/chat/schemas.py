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
        return cls(
            uid=session.id,
            name="New Session ...",
            messages=session.messages,
            created_at=session.startDate,
        )


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
