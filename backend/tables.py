import sqlalchemy

# import databases


# database = databases.Database("sqlite://guitarlette.db")
metadata = sqlalchemy.MetaData()
user_table = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String(length=100)),
    sqlalchemy.Column("content", sqlalchemy.String(length=100)),
)
