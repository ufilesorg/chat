from enum import Enum


class AIEngines(str, Enum):
    gpt_4o = "gpt-4o"
    gpt_4o_mini = "gpt-4o-mini"
    claude_3_5_sonnet = "claude-3-5-sonnet"
    gemini_1_5_flash = "gemini-1-5-flash"
    gemini_2_flash = "gemini-2-flash"
    grok = "grok"
    deepseek = "deepseek"
    deepseek_reasoner = "deepseek_reasoner"
    # gpt_4_turbo = "gpt-4-turbo"
    # gpt_4 = "gpt-4"
    # gpt35turbo = "gpt-3.5-turbo"
    # claud3haiku = "claud-3-haiku"
    # claud3opus = "claud-3-opus"
    # claud3sonnet = "claud-3-sonnet"

    @classmethod
    def default(cls):
        return cls.gpt_4o

    @property
    def _info(self):
        return {
            AIEngines.gpt_4o: {
                "metis_bot_id": "55d1e911-67f1-493c-b4ff-bbafcca0e26b",
                "thumbnail_url": "https://upload.wikimedia.org/wikipedia/commons/e/ef/ChatGPT-Logo.svg",
                "price": 1.1,
                "input_token_price": 0.27,
                "output_token_price": 1.1,
                "max_tokens": 16384,
            },
            AIEngines.gpt_4o_mini: {
                "metis_bot_id": "b6eff700-4cde-4407-93e6-0a93de7db61d",
                "thumbnail_url": "https://upload.wikimedia.org/wikipedia/commons/e/ef/ChatGPT-Logo.svg",
                "price": 0.07,
                "input_token_price": 0.02,
                "output_token_price": 0.07,
                "max_tokens": 16384,
            },
            AIEngines.claude_3_5_sonnet: {
                "metis_bot_id": "0ff81eed-abd4-4627-846f-15eae7d21c99",
                "thumbnail_url": "https://www.anthropic.com/images/icons/safari-pinned-tab.svg",
                "price": 1.65,
                "input_token_price": 0.33,
                "output_token_price": 1.65,
                "max_tokens": 16384,
            },
            AIEngines.gemini_1_5_flash: {
                "metis_bot_id": "7c8371dc-29cd-4a99-b835-f17cdb8adf36",
                "thumbnail_url": "https://www.gstatic.com/lamda/images/gemini_favicon_f069958c85030456e93de685481c559f160ea06b.png",
                "price": 0.03,
                "input_token_price": 0.001,
                "output_token_price": 0.003,
                "max_tokens": 16384,
            },
            AIEngines.gemini_2_flash: {
                "metis_bot_id": "c928bda6-442d-43ed-a3d4-5aef923fb0f5",
                "thumbnail_url": "https://www.gstatic.com/lamda/images/gemini_favicon_f069958c85030456e93de685481c559f160ea06b.png",
                "price": 0.03,
                "input_token_price": 0.001,
                "output_token_price": 0.004,
                "max_tokens": 16384,
            },
            AIEngines.grok: {
                "metis_bot_id": "68fe569d-323e-4a14-b8e9-fd1ee3527881",
                "thumbnail_url": "https://x.ai/icon.svg?2f55916d3a05ba17",
                "price": 1.1,
                "input_token_price": 0.22,
                "output_token_price": 1.1,
                "max_tokens": 16384,
            },
            AIEngines.deepseek: {
                "metis_bot_id": "1ef1bb12-1a57-42e1-983b-1381527372de",
                "thumbnail_url": "https://media.pixiee.io/v1/f/ffa4c743-c873-437d-936c-e20c38b1f870/deepseek.webp",
                "price": 0.1,
                "input_token_price": 0.1,
                "output_token_price": 0.3,
                "max_tokens": 16384,
            },
            AIEngines.deepseek_reasoner: {
                "metis_bot_id": "04d5b270-3cbb-465f-8b07-49c2157fdc5c",
                "thumbnail_url": "https://media.pixiee.io/v1/f/ffa4c743-c873-437d-936c-e20c38b1f870/deepseek.webp",
                "price": 0.1,
                "input_token_price": 0.1,
                "output_token_price": 0.3,
                "max_tokens": 16384,
            },
        }[self]

    @classmethod
    def from_metis_bot_id(cls, bot_id: str):
        for engine in cls:
            if engine.metis_bot_id == bot_id:
                return engine
        return cls.default()

    @property
    def metis_bot_id(self):
        return self._info["metis_bot_id"]

    @property
    def thumbnail_url(self):
        return self._info["thumbnail_url"]

    @property
    def price(self):
        return self._info["price"]

    @property
    def input_token_price(self):
        return self._info["input_token_price"]

    @property
    def output_token_price(self):
        return self._info["output_token_price"]

    @property
    def max_tokens(self):
        return self._info["max_tokens"]
