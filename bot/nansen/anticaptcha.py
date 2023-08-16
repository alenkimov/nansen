from bot.anticaptcha import solve_recaptcha_v2


URL = "https://www.nansen.ai/early-access"
SITE_KEY = "6LcnRGwnAAAAAH-fdJFy0hD3e4GeYxWkMcbkCwi2"


async def solve() -> str:
    return await solve_recaptcha_v2(URL, SITE_KEY)

