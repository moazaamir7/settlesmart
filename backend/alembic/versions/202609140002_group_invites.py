"""group invites

Revision ID: 202609140002
Revises: 202609140001
Create Date: 2026-09-14 01:05:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "202609140002"
down_revision: Union[str, None] = "202609140001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "group_invites",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("group_id", sa.String(length=36), nullable=False),
        sa.Column("token", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_group_invites_group_id"), "group_invites", ["group_id"], unique=False)
    op.create_index(op.f("ix_group_invites_token"), "group_invites", ["token"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_group_invites_token"), table_name="group_invites")
    op.drop_index(op.f("ix_group_invites_group_id"), table_name="group_invites")
    op.drop_table("group_invites")
