from fastapi_mongo_base.core.enums import Language
from fastapi_mongo_base.models import OwnedEntity

from .ai import AIEngines


class Session(OwnedEntity):
    engine: AIEngines
    name: str | None = None
    language: Language | None = None

    class Settings:
        indexes = OwnedEntity.Settings.indexes
