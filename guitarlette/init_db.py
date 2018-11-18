from tortoise import Tortoise, run_async
from guitarlette.config import DB_CONFIG


async def init():
    await Tortoise.init(**DB_CONFIG)
    await Tortoise.generate_schemas()


run_async(init())
