"""owner and soft remove participants

Revision ID: 202609140003
Revises: 202609140002
Create Date: 2026-09-14 01:25:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "202609140003"
down_revision: Union[str, None] = "202609140002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "participants",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column("groups", sa.Column("owner_participant_id", sa.String(length=36), nullable=True))
    op.execute(
        """
        UPDATE groups
        SET owner_participant_id = first_participant.id
        FROM (
            SELECT DISTINCT ON (group_id) id, group_id
            FROM participants
            WHERE is_active IS TRUE
            ORDER BY group_id, created_at ASC
        ) AS first_participant
        WHERE groups.id = first_participant.group_id
        """
    )
    op.create_foreign_key(
        "fk_groups_owner_participant_id_participants",
        "groups",
        "participants",
        ["owner_participant_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.alter_column("participants", "is_active", server_default=None)


def downgrade() -> None:
    op.drop_constraint("fk_groups_owner_participant_id_participants", "groups", type_="foreignkey")
    op.drop_column("groups", "owner_participant_id")
    op.drop_column("participants", "is_active")
