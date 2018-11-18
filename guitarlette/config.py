class Config:

    DEBUG: bool = False
    DATABASE: dict = {
        "db_url": "sqlite://guitarlette.db",
        "modules": {"models": ["guitarlette.models"]},
    }
    TEMPLATE_DIR = "templates"
    STATIC_DIR = "static"
