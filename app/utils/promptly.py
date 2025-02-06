import os

import httpx
from fastapi_mongo_base.utils import basic


class PromptlyClient(httpx.AsyncClient):
    def __init__(self):
        super().__init__(
            base_url=os.getenv("PROMPTLY_URL"),
            headers={
                "accept": "application/json",
                "Content-Type": "application/json",
                "x-api-key": os.getenv("PROMPTLY_API_KEY"),
            },
        )

    @basic.try_except_wrapper
    @basic.retry_execution(attempts=3, delay=1)
    async def ai_image(
        self, image_url: str, key: str, data: dict = {}, **kwargs
    ) -> dict:
        kwargs["timeout"] = kwargs.get("timeout", None)
        r = await self.post(
            f"/image/{key}", json={**data, "image_url": image_url}, **kwargs
        )
        r.raise_for_status()
        return r.json()

    @basic.try_except_wrapper
    @basic.retry_execution(attempts=3, delay=1)
    async def ai(self, key: str, data: dict = {}, **kwargs) -> dict:
        kwargs["timeout"] = kwargs.get("timeout", None)
        r = await self.post(f"/{key}", json=data, **kwargs)
        r.raise_for_status()
        return r.json()

    @basic.try_except_wrapper
    @basic.retry_execution(attempts=3, delay=1)
    async def ai_search(self, key: str, data: dict = {}, **kwargs) -> dict:
        return await self.ai(f"/search/{key}", data, **kwargs)

    @basic.try_except_wrapper
    @basic.retry_execution(attempts=3, delay=1)
    async def translate(self, text: str, target_language: str = "en", **kwargs) -> str:
        resp: dict = await self.ai(
            "translate", {"text": text, "target_language": target_language}, **kwargs
        )
        return resp.get("translated_text")
