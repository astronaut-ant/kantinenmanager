"""update user_id on refresh_token_session

Revision ID: 9e9c52518be2
Revises: 20dc842ffb79
Create Date: 2025-03-05 08:21:00.833782

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9e9c52518be2"
down_revision: Union[str, None] = "20dc842ffb79"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DELETE FROM refresh_token_session")
    op.create_foreign_key(
        "fk_refresh_token_user",
        "refresh_token_session",
        "user",
        ["user_id"],
        ["id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
        use_alter=True,
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_refresh_token_user", "refresh_token_session", type_="foreignkey"
    )
