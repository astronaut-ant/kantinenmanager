"""add person.hidden and group.group_number

Revision ID: f0881fc0bca6
Revises: 8623f646b5fd
Create Date: 2025-01-21 20:40:26.458517

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f0881fc0bca6"
down_revision: Union[str, None] = "8623f646b5fd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "group",
        sa.Column("group_number", sa.Integer, nullable=True),
    )
    op.add_column(
        "person",
        sa.Column("hidden", sa.Boolean(), nullable=False, server_default="false"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("person", "hidden")
    op.drop_column("group", "group_number")
    # ### end Alembic commands ###
