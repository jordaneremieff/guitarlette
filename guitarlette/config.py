from dataclasses import dataclass, field


@dataclass
class Config:

    DEBUG: bool = False
    DATABASE: dict = field(default_factory=dict)
    TEMPLATE_DIR: str = None
    STATIC_DIR: str = None
