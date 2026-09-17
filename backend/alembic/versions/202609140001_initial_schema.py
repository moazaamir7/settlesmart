"""initial schema

Revision ID: 202609140001
Revises:
Create Date: 2026-09-14 00:01:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "202609140001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "groups",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "participants",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("group_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_participants_group_id"), "participants", ["group_id"], unique=False)
    op.create_table(
        "expenses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("group_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("payer_id", sa.String(length=36), nullable=False),
        sa.Column("subtotal_cents", sa.Integer(), nullable=False),
        sa.Column("tax_cents", sa.Integer(), nullable=False),
        sa.Column("tip_cents", sa.Integer(), nullable=False),
        sa.Column("fees_cents", sa.Integer(), nullable=False),
        sa.Column("discounts_cents", sa.Integer(), nullable=False),
        sa.Column("total_cents", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("split_method", sa.String(length=30), nullable=False),
        sa.Column("source", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["payer_id"], ["participants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_expenses_group_id"), "expenses", ["group_id"], unique=False)
    op.create_table(
        "expense_participants",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("expense_id", sa.String(length=36), nullable=False),
        sa.Column("participant_id", sa.String(length=36), nullable=False),
        sa.Column("share_cents", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["expense_id"], ["expenses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["participant_id"], ["participants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("expense_id", "participant_id", name="uq_expense_participant"),
    )
    op.create_index(op.f("ix_expense_participants_expense_id"), "expense_participants", ["expense_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_expense_participants_expense_id"), table_name="expense_participants")
    op.drop_table("expense_participants")
    op.drop_index(op.f("ix_expenses_group_id"), table_name="expenses")
    op.drop_table("expenses")
    op.drop_index(op.f("ix_participants_group_id"), table_name="participants")
    op.drop_table("participants")
    op.drop_table("groups")
