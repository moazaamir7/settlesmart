"""admin auth and group settings

Revision ID: 202609140005
Revises: 202609140004
Create Date: 2026-09-14 06:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "202609140005"
down_revision: Union[str, None] = "202609140004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admin_users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("settlement_contact", sa.String(length=160), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_admin_users_email"), "admin_users", ["email"], unique=True)
    op.create_table(
        "admin_sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("admin_id", sa.String(length=36), nullable=False),
        sa.Column("token", sa.String(length=96), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["admin_id"], ["admin_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_admin_sessions_admin_id"), "admin_sessions", ["admin_id"], unique=False)
    op.create_index(op.f("ix_admin_sessions_token"), "admin_sessions", ["token"], unique=True)
    op.add_column("groups", sa.Column("admin_id", sa.String(length=36), nullable=True))
    op.add_column("groups", sa.Column("settlement_contact", sa.String(length=160), nullable=False, server_default=""))
    op.create_index(op.f("ix_groups_admin_id"), "groups", ["admin_id"], unique=False)
    op.create_foreign_key("fk_groups_admin_id_admin_users", "groups", "admin_users", ["admin_id"], ["id"], ondelete="CASCADE")
    op.alter_column("groups", "settlement_contact", server_default=None)
    op.alter_column("admin_users", "settlement_contact", server_default=None)


def downgrade() -> None:
    op.drop_constraint("fk_groups_admin_id_admin_users", "groups", type_="foreignkey")
    op.drop_index(op.f("ix_groups_admin_id"), table_name="groups")
    op.drop_column("groups", "settlement_contact")
    op.drop_column("groups", "admin_id")
    op.drop_index(op.f("ix_admin_sessions_token"), table_name="admin_sessions")
    op.drop_index(op.f("ix_admin_sessions_admin_id"), table_name="admin_sessions")
    op.drop_table("admin_sessions")
    op.drop_index(op.f("ix_admin_users_email"), table_name="admin_users")
    op.drop_table("admin_users")
