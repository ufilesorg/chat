from enum import Enum


class AIEngines(str, Enum):
    gpt_4o = "gpt-4o"
    gpt_4o_mini = "gpt-4o-mini"
    # gpt_4_turbo = "gpt-4-turbo"
    # gpt_4 = "gpt-4"
    # gpt35turbo = "gpt-3.5-turbo"
    # claud3opus = "claud-3-opus"
    # claud3sonnet = "claud-3-sonnet"
    claud35sonnet = "claud-3-5-sonnet"
    # claud3haiku = "claud-3-haiku"
    gemini_1_5_flash = "gemini-1-5-flash"
    grok = "grok"
    deepseek = "deepseek"
    deepseek_reasoner = "deepseek_reasoner"

    @classmethod
    def default(cls):
        return cls.gpt_4o

    @classmethod
    def from_metis_bot_id(cls, bot_id: str):
        for engine in cls:
            if engine.metis_bot_id == bot_id:
                return engine
        return cls.default()

    @property
    def metis_bot_id(self):
        return {
            AIEngines.gpt_4o: "55d1e911-67f1-493c-b4ff-bbafcca0e26b",
            AIEngines.gpt_4o_mini: "b6eff700-4cde-4407-93e6-0a93de7db61d",
            # AIEngines.gpt_4_turbo: "3e0640f3-286e-4c4d-abea-0993d522771f",
            # AIEngines.gpt_4: "288f04e2-728d-4be4-af0b-83ae1b97b87a",
            # AIEngines.gpt35turbo: "03d99ad7-e344-4b0c-bbf5-46609f47d937",
            # AIEngines.claud3opus: "0f87bb21-2357-49a4-a80d-d2f944b89671",
            # AIEngines.claud3sonnet: "f9402e09-18b7-49e9-b08b-ad8bd8836511",
            AIEngines.claud35sonnet: "0ff81eed-abd4-4627-846f-15eae7d21c99",
            # AIEngines.claud3haiku: "2db268fe-914c-469e-b597-9ed46dc0f0f3",
            AIEngines.gemini_1_5_flash: "7c8371dc-29cd-4a99-b835-f17cdb8adf36",
            AIEngines.grok: "68fe569d-323e-4a14-b8e9-fd1ee3527881",
            AIEngines.deepseek: "1ef1bb12-1a57-42e1-983b-1381527372de",
            AIEngines.deepseek_reasoner: "04d5b270-3cbb-465f-8b07-49c2157fdc5c",
            # AIEngines.gpt_4o: "c5a435e6-335b-419a-8386-41247bb6a359",
        }[self]

    @property
    def thumbnail_url(self):
        return {
            AIEngines.gpt_4o: "https://upload.wikimedia.org/wikipedia/commons/e/ef/ChatGPT-Logo.svg",
            AIEngines.gpt_4o_mini: "https://upload.wikimedia.org/wikipedia/commons/e/ef/ChatGPT-Logo.svg",
            # AIEngines.gpt_4_turbo: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/ChatGPT_logo.svg/512px-ChatGPT_logo.svg.png",
            # AIEngines.gpt_4: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/ChatGPT_logo.svg/512px-ChatGPT_logo.svg.png",
            # AIEngines.gpt35turbo: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/ChatGPT_logo.svg/512px-ChatGPT_logo.svg.png",
            # AIEngines.claud3opus: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/ChatGPT_logo.svg/512px-ChatGPT_logo.svg.png",
            # AIEngines.claud3sonnet: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/ChatGPT_logo.svg/512px-ChatGPT_logo.svg.png",
            AIEngines.claud35sonnet: "https://www.anthropic.com/images/icons/safari-pinned-tab.svg",
            # AIEngines.claud3haiku: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/ChatGPT_logo.svg/512px-ChatGPT_logo.svg.png",
            AIEngines.gemini_1_5_flash: "https://www.gstatic.com/lamda/images/gemini_favicon_f069958c85030456e93de685481c559f160ea06b.png",
            AIEngines.grok: "https://x.ai/icon.svg?2f55916d3a05ba17",
            AIEngines.deepseek: "https://www.deepseek.com/favicon.ico",
            AIEngines.deepseek_reasoner: "https://www.deepseek.com/favicon.ico",
        }[self]

    @property
    def price(self):
        return {
            AIEngines.gpt_4o: 11,
            AIEngines.gpt_4o_mini: 0.7,
            # AIEngines.gpt_4_turbo: 33,
            # AIEngines.gpt_4: 66,
            # AIEngines.gpt35turbo: 1.7,
            # AIEngines.claud3opus: 82.50,
            # AIEngines.claud3sonnet: 16.50,
            AIEngines.claud35sonnet: 16.50,
            # AIEngines.claud3haiku: 1.4,
            AIEngines.gemini_1_5_flash: 0.30,
            AIEngines.grok: 11,
            AIEngines.deepseek: 1,
            AIEngines.deepseek_reasoner: 1,
        }[self]
