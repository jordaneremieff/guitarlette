"""Make artist name unique

Revision ID: afae8e569ad8
Revises: 78685c029fb5
Create Date: 2019-08-31 12:32:55.760872

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "afae8e569ad8"
down_revision = "78685c029fb5"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(None, "artists", ["name"])


def downgrade():
    op.drop_constraint(None, "artists", type_="unique")
