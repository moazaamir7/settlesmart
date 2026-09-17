"""group messages

Revision ID: 202609140004
Revises: 202609140003
Create Date: 2026-09-14 01:35:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "202609140004"
down_revision: Union[str, None] = "202609140003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "group_messages",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("group_id", sa.String(length=36), nullable=False),
        sa.Column("sender_name", sa.String(length=120), nullable=False),
        sa.Column("body", sa.String(length=1000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_group_messages_group_id"), "group_messages", ["group_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_group_messages_group_id"), table_name="group_messages")
    op.drop_table("group_messages")
