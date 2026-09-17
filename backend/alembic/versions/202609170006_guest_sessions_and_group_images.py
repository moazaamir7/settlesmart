"""guest sessions and group images

Revision ID: 202609170006
Revises: 202609140005
Create Date: 2026-09-17 14:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "202609170006"
down_revision: Union[str, None] = "202609140005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("groups", sa.Column("image_url", sa.String(length=255), nullable=True))
    op.create_table(
        "guest_sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("group_id", sa.String(length=36), nullable=False),
        sa.Column("participant_id", sa.String(length=36), nullable=False),
        sa.Column("token", sa.String(length=96), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["participant_id"], ["participants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_guest_sessions_group_id"), "guest_sessions", ["group_id"], unique=False)
    op.create_index(op.f("ix_guest_sessions_participant_id"), "guest_sessions", ["participant_id"], unique=False)
    op.create_index(op.f("ix_guest_sessions_token"), "guest_sessions", ["token"], unique=True)
    op.create_check_constraint("ck_groups_currency_supported", "groups", "currency IN ('CAD', 'USD')")


def downgrade() -> None:
    op.drop_constraint("ck_groups_currency_supported", "groups", type_="check")
    op.drop_index(op.f("ix_guest_sessions_token"), table_name="guest_sessions")
    op.drop_index(op.f("ix_guest_sessions_participant_id"), table_name="guest_sessions")
    op.drop_index(op.f("ix_guest_sessions_group_id"), table_name="guest_sessions")
    op.drop_table("guest_sessions")
    op.drop_column("groups", "image_url")
