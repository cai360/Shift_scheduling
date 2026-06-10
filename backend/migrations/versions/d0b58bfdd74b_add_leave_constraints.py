"""add_leave_constraints

Revision ID: d0b58bfdd74b
Revises: 0bf19154c081
Create Date: 2026-06-10 16:24:15.891947

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0b58bfdd74b'
down_revision = '0bf19154c081'
branch_labels = None
depends_on = None


def upgrade():
    op.create_check_constraint(
        "ck_leave_type",
        "leaves",
        "type IN ('sick', 'annual', 'personal')"
    )

    op.create_check_constraint(
        "ck_reject_reason_required",
        "leaves",
        """
        (status = 'rejected' AND reject_reason IS NOT NULL)
        OR
        (status != 'rejected' AND reject_reason IS NULL)
        """
    )

    op.create_check_constraint(
        "ck_approval_consistency",
        "leaves",
        """
        (status IN ('approved', 'rejected')
         AND reviewed_at IS NOT NULL
         AND reviewed_by IS NOT NULL)
        OR
        (status IN ('pending', 'withdrawn')
         AND reviewed_at IS NULL
         AND reviewed_by IS NULL)
        """
    )

    op.create_check_constraint(
        "ck_leave_range_valid",
        "leaves",
        "start_at < end_at"
    )


def downgrade():
    pass
