"""add shift time order check constraint

Revision ID: 46bf0e5c9fc4
Revises: 10279fb407bf
Create Date: 2026-03-19 10:36:14.166376

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '46bf0e5c9fc4'
down_revision = '10279fb407bf'
branch_labels = None
depends_on = None


def upgrade():
    op.create_check_constraint(
        'ck_shift_time_order',
        'shifts',
        'end_at > start_at' 
    )


def downgrade():
    op.drop_constraint(
        'ck_shift_time_order',
        'shifts',
        type_='check'
    )
