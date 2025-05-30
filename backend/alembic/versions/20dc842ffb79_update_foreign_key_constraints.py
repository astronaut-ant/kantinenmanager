"""update foreign key constraints

Revision ID: 20dc842ffb79
Revises: 7f07dd7d8fd9
Create Date: 2025-03-05 08:15:44.515827

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20dc842ffb79"
down_revision: Union[str, None] = "7f07dd7d8fd9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("fk_employee_group", "employee", type_="foreignkey")
    op.create_foreign_key(
        "fk_employee_group",
        "employee",
        "group",
        ["group_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("fk_employee_group", "employee", type_="foreignkey")
    op.create_foreign_key(
        "fk_employee_group",
        "employee",
        "group",
        ["group_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="SET NULL",
    )
    # ### end Alembic commands ###
