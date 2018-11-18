from tortoise import Tortoise, run_async
from guitarlette.config import Config

config = Config()


async def init():
    await Tortoise.init(**config.DATABASE)
    await Tortoise.generate_schemas()


run_async(init())
