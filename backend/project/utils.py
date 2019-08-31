import os


def get_db_url():
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "")
    server = os.getenv("POSTGRES_SERVER", "localhost")
    db = os.getenv("POSTGRES_DB", "guitarlette")
    return f"postgresql://{user}:{password}@{server}/{db}"
