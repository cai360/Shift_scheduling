"""add unique active shift slot index

Revision ID: 1b4173b734af
Revises: 472f201c1459
Create Date: 2026-07-13 23:13:50.690541

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b4173b734af'
down_revision = '472f201c1459'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        'uq_shift_company_slot',
        'shifts',
        ['company_id', 'start_at', 'end_at'],
        unique=True,
        postgresql_where=sa.text('deleted_at IS NULL'),
    )


def downgrade():
    op.drop_index(
        'uq_shift_company_slot',
        table_name='shifts',
    )
