import sys
import os
import contextlib

from tortoise import Tortoise, run_async

DATABASE_URL = "sqlite://guitarlette.db"


async def init():
    msg = "".join(
        [
            f"This command will create a new database: 'guitarlette.db', ",
            "any existing database will be DESTROYED...\n\nEnter 'yes' to continue.\n",
        ]
    )
    confirm = input(msg)
    if confirm != "yes":
        sys.exit()

    with contextlib.suppress(FileNotFoundError):
        os.remove("guitarlette.db")

    await Tortoise.init(db_url=DATABASE_URL, modules={"models": ["guitarlette.models"]})
    await Tortoise.generate_schemas()


run_async(init())
