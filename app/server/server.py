from apps.chat.routes import router as chat_router
from fastapi_mongo_base.core import app_factory

from . import config

app = app_factory.create_app(
    settings=config.Settings(),
    origins=[
        "http://localhost:8000",
        "http://localhost:3000",
        "https://pixiee.io",
        "https://dev.pixiee.io",
        "https://studio.pixiee.io",
        "https://pixy.ir",
        "https://studio.pixy.ir",
        "https://dev.pixy.ir",
        "capacitor://localhost",
        "http://localhost",
        "https://localhost",
    ],
)
app.include_router(chat_router, prefix=f"{config.Settings.base_path}")
