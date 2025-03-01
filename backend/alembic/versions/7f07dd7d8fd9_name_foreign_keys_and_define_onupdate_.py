"""name foreign keys and define onupdate and ondelete

Revision ID: 7f07dd7d8fd9
Revises: 74da865448a0
Create Date: 2025-03-01 14:44:39.737795

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7f07dd7d8fd9"
down_revision: Union[str, None] = "74da865448a0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # fmt: off
    op.drop_constraint('daily_order_location_id_fkey', 'daily_order', type_='foreignkey')
    op.drop_constraint('daily_order_person_id_fkey', 'daily_order', type_='foreignkey')
    op.create_foreign_key('fk_dailyorder_person', 'daily_order', 'person', ['person_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    op.create_foreign_key('fk_dailyorder_location', 'daily_order', 'location', ['location_id'], ['id'], onupdate='CASCADE', ondelete='SET NULL')
    op.drop_constraint('employee_id_fkey', 'employee', type_='foreignkey')
    op.drop_constraint('employee_group_id_fkey', 'employee', type_='foreignkey')
    op.create_foreign_key('fk_employee_group', 'employee', 'group', ['group_id'], ['id'], onupdate='CASCADE', ondelete='SET NULL')
    op.create_foreign_key('fk_employee_person', 'employee', 'person', ['id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    op.drop_constraint('group_location_id_fkey', 'group', type_='foreignkey')
    op.drop_constraint('group_user_id_replacement_fkey', 'group', type_='foreignkey')
    op.drop_constraint('group_user_id_group_leader_fkey', 'group', type_='foreignkey')
    op.create_foreign_key('fk_group_location', 'group', 'location', ['location_id'], ['id'], onupdate='CASCADE', ondelete='SET NULL')
    op.create_foreign_key('fk_group_group_leader', 'group', 'user', ['user_id_group_leader'], ['id'], onupdate='CASCADE', ondelete='SET NULL')
    op.create_foreign_key('fk_group_replacement', 'group', 'user', ['user_id_replacement'], ['id'], onupdate='CASCADE', ondelete='SET NULL')
    op.drop_constraint('location_user_id_location_leader_fkey', 'location', type_='foreignkey')
    op.create_foreign_key('fk_location_location_leader', 'location', 'user', ['user_id_location_leader'], ['id'], onupdate='CASCADE', ondelete='SET NULL')
    op.drop_constraint('old_order_person_id_fkey', 'old_order', type_='foreignkey')
    op.drop_constraint('old_order_location_id_fkey', 'old_order', type_='foreignkey')
    op.create_foreign_key('fk_oldorder_person', 'old_order', 'person', ['person_id'], ['id'], onupdate='CASCADE', ondelete='SET NULL')
    op.create_foreign_key('fk_oldorder_location', 'old_order', 'location', ['location_id'], ['id'], onupdate='CASCADE', ondelete='SET NULL')
    op.drop_constraint('pre_order_person_id_fkey', 'pre_order', type_='foreignkey')
    op.drop_constraint('pre_order_location_id_fkey', 'pre_order', type_='foreignkey')
    op.create_foreign_key('fk_preorder_person', 'pre_order', 'person', ['person_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    op.create_foreign_key('fk_preorder_location', 'pre_order', 'location', ['location_id'], ['id'], onupdate='CASCADE', ondelete='SET NULL')
    op.drop_constraint('user_id_fkey', 'user', type_='foreignkey')
    op.drop_constraint('user_location_id_fkey', 'user', type_='foreignkey')
    op.create_foreign_key('fk_user_location', 'user', 'location', ['location_id'], ['id'], onupdate='CASCADE', ondelete='SET NULL', use_alter=True)
    op.create_foreign_key('fk_user_person', 'user', 'person', ['id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    # fmt: on


def downgrade() -> None:
    # fmt: off
    op.drop_constraint('fk_user_person', 'user', type_='foreignkey')
    op.drop_constraint('fk_user_location', 'user', type_='foreignkey')
    op.create_foreign_key('user_location_id_fkey', 'user', 'location', ['location_id'], ['id'])
    op.create_foreign_key('user_id_fkey', 'user', 'person', ['id'], ['id'])
    op.drop_constraint('fk_preorder_location', 'pre_order', type_='foreignkey')
    op.drop_constraint('fk_preorder_person', 'pre_order', type_='foreignkey')
    op.create_foreign_key('pre_order_location_id_fkey', 'pre_order', 'location', ['location_id'], ['id'])
    op.create_foreign_key('pre_order_person_id_fkey', 'pre_order', 'person', ['person_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('fk_oldorder_location', 'old_order', type_='foreignkey')
    op.drop_constraint('fk_oldorder_person', 'old_order', type_='foreignkey')
    op.create_foreign_key('old_order_location_id_fkey', 'old_order', 'location', ['location_id'], ['id'])
    op.create_foreign_key('old_order_person_id_fkey', 'old_order', 'person', ['person_id'], ['id'], ondelete='SET NULL')
    op.drop_constraint('fk_location_location_leader', 'location', type_='foreignkey')
    op.create_foreign_key('location_user_id_location_leader_fkey', 'location', 'user', ['user_id_location_leader'], ['id'])
    op.drop_constraint('fk_group_replacement', 'group', type_='foreignkey')
    op.drop_constraint('fk_group_group_leader', 'group', type_='foreignkey')
    op.drop_constraint('fk_group_location', 'group', type_='foreignkey')
    op.create_foreign_key('group_user_id_group_leader_fkey', 'group', 'user', ['user_id_group_leader'], ['id'])
    op.create_foreign_key('group_user_id_replacement_fkey', 'group', 'user', ['user_id_replacement'], ['id'])
    op.create_foreign_key('group_location_id_fkey', 'group', 'location', ['location_id'], ['id'])
    op.drop_constraint('fk_employee_person', 'employee', type_='foreignkey')
    op.drop_constraint('fk_employee_group', 'employee', type_='foreignkey')
    op.create_foreign_key('employee_group_id_fkey', 'employee', 'group', ['group_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('employee_id_fkey', 'employee', 'person', ['id'], ['id'])
    op.drop_constraint('fk_dailyorder_location', 'daily_order', type_='foreignkey')
    op.drop_constraint('fk_dailyorder_person', 'daily_order', type_='foreignkey')
    op.create_foreign_key('daily_order_person_id_fkey', 'daily_order', 'person', ['person_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('daily_order_location_id_fkey', 'daily_order', 'location', ['location_id'], ['id'])
    # fmt: on
