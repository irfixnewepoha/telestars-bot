"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-11-02
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=True),
        sa.Column("first_name", sa.String(length=128), nullable=True),
        sa.Column("balance_kop", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_banned", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("balance_kop >= 0", name="ck_users_balance_nonneg"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=False)

    op.create_table(
        "settings",
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("value", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )

    op.create_table(
        "rate_snapshots",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ton_rub", sa.Float(), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rate_snapshots_ts"), "rate_snapshots", ["ts"], unique=False)

    op.create_table(
        "admin_audit",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("admin_id", sa.BigInteger(), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ts", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("recipient_username", sa.String(length=64), nullable=False),
        sa.Column("stars_amount", sa.Integer(), nullable=False),
        sa.Column("price_kop", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "created",
                "awaiting_payment",
                "paid",
                "fulfilling",
                "completed",
                "expired",
                "failed_refunded",
                "manual_review",
                "cancelled",
                name="order_status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("fragment_ref_id", sa.String(length=128), nullable=True),
        sa.Column("platega_tx_id", sa.String(length=64), nullable=True),
        sa.Column("cost_ton_nano", sa.BigInteger(), nullable=True),
        sa.Column("ton_tx_hash", sa.String(length=128), nullable=True),
        sa.Column("fail_reason", sa.Text(), nullable=True),
        sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("stars_amount > 0", name="ck_orders_stars_positive"),
        sa.CheckConstraint("price_kop >= 0", name="ck_orders_price_nonneg"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fragment_ref_id"),
        sa.UniqueConstraint("platega_tx_id"),
    )
    op.create_index(op.f("ix_orders_status"), "orders", ["status"], unique=False)
    op.create_index(op.f("ix_orders_user_id"), "orders", ["user_id"], unique=False)
    op.create_index("ix_orders_status_next_attempt", "orders", ["status", "next_attempt_at"], unique=False)

    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=32), server_default="platega", nullable=False),
        sa.Column("provider_tx_id", sa.String(length=64), nullable=False),
        sa.Column("amount_kop", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "confirmed",
                "canceled",
                "chargebacked",
                name="payment_status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("raw_callback", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "provider_tx_id", name="uq_payments_provider_tx"),
    )
    op.create_index(op.f("ix_payments_order_id"), "payments", ["order_id"], unique=False)

    op.create_table(
        "balance_ledger",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("delta_kop", sa.Integer(), nullable=False),
        sa.Column(
            "reason",
            sa.Enum(
                "refund",
                "overpay",
                "admin",
                "order_payment",
                "balance_payment",
                name="ledger_reason",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_balance_ledger_user_id"), "balance_ledger", ["user_id"], unique=False)

    op.create_table(
        "order_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("from_status", sa.String(length=32), nullable=True),
        sa.Column("to_status", sa.String(length=32), nullable=False),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_order_events_order_id"), "order_events", ["order_id"], unique=False)


def downgrade() -> None:
    op.drop_table("order_events")
    op.drop_table("balance_ledger")
    op.drop_table("payments")
    op.drop_table("orders")
    op.drop_table("admin_audit")
    op.drop_table("rate_snapshots")
    op.drop_table("settings")
    op.drop_table("users")
