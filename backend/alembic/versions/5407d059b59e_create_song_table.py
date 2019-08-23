"""Create song table

Revision ID: 5407d059b59e
Revises:
Create Date: 2019-08-24 09:12:47.586397

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5407d059b59e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "songs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("artist", sa.String(100), nullable=False),
        sa.Column("content", sa.Text, nullable=True),
    )


def downgrade():
    op.drop_table("songs")
