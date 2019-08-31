"""Add artist table, update field lengths, remove artist string field from song table

Revision ID: 91660e97dd4f
Revises: 4c10f618570b
Create Date: 2019-08-31 12:24:58.574809

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "91660e97dd4f"
down_revision = "4c10f618570b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "artists",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_column("songs", "artist")


def downgrade():
    op.add_column(
        "songs",
        sa.Column(
            "artist", sa.VARCHAR(length=100), autoincrement=False, nullable=False
        ),
    )
    op.drop_table("artists")
