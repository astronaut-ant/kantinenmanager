"""added the attribute 'nothing' to the models pre_orders, daily_orders and old_orders, also added cascade='all, delete-orphans' to the person-order relationships

Revision ID: 68684692b315
Revises: aa0dd6eb0e8c
Create Date: 2024-12-12 11:09:35.705083

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "68684692b315"
down_revision: Union[str, None] = "aa0dd6eb0e8c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("daily_order", sa.Column("nothing", sa.Boolean(), nullable=True))
    op.add_column("old_order", sa.Column("nothing", sa.Boolean(), nullable=True))
    op.add_column("pre_order", sa.Column("nothing", sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("pre_order", "nothing")
    op.drop_column("old_order", "nothing")
    op.drop_column("daily_order", "nothing")
    # ### end Alembic commands ###
