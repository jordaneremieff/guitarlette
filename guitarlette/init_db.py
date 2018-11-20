import sys
import os
import contextlib

from tortoise import Tortoise, run_async
from guitarlette.app.settings import DATABASE, DATABASE_NAME


async def init():
    msg = "".join(
        [
            f"This command will create a new database: '{DATABASE_NAME}.db', ",
            "any existing database will be DESTROYED...\n\nEnter 'yes' to continue.\n",
        ]
    )
    confirm = input(msg)
    if confirm != "yes":
        sys.exit()

    with contextlib.suppress(FileNotFoundError):
        os.remove(f"{DATABASE_NAME}.db")

    await Tortoise.init(**DATABASE)
    await Tortoise.generate_schemas()


run_async(init())
