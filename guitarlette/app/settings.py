import os


class Config:

    APP_DIR = os.path.dirname(os.path.realpath(__file__))

    DEBUG = True

    DATABASE_NAME = "app"

    DATABASE = {
        "db_url": f"sqlite://{DATABASE_NAME}.db",
        "modules": {"models": ["guitarlette.models"]},
    }

    TEMPLATE_DIR = os.path.join(APP_DIR, "templates")

    STATIC_DIR = os.path.join(APP_DIR, "static")

    WEBSOCKET_URL = "ws://127.0.0.1:8000/ws"
