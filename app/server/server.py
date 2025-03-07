from apps.chat.routes import router as chat_router
from fastapi_mongo_base.core import app_factory

from . import config

app = app_factory.create_app(settings=config.Settings(), origins=["https://pixy.ir"])
app.include_router(chat_router, prefix=f"{config.Settings.base_path}")
