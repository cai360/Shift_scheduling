"""add owner into company_users role constraint

Revision ID: b4c6703e3f69
Revises: b37618f851a8
Create Date: 2026-03-06 15:29:03.928447

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4c6703e3f69'
down_revision = 'b37618f851a8'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("company_users", schema=None) as batch_op:
        batch_op.drop_constraint("ck_company_users_role", type_="check")
        batch_op.create_check_constraint(
            "ck_company_users_role",
            "role IN ('owner','manager','employee')"
        )


def downgrade():
    with op.batch_alter_table("company_users", schema=None) as batch_op:
        batch_op.drop_constraint("ck_company_users_role", type_="check")
        batch_op.create_check_constraint(
            "ck_company_users_role",
            "role IN ('manager','employee')"
        )