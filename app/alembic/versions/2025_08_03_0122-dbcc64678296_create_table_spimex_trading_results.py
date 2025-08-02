"""create table spimex_trading_results

Revision ID: dbcc64678296
Revises: 
Create Date: 2025-08-03 01:22:29.555165

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "dbcc64678296"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "spimex_trading_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "exchange_product_id", sa.String(length=100), nullable=False
        ),
        sa.Column(
            "exchange_product_name", sa.String(length=300), nullable=False
        ),
        sa.Column("oil_id", sa.String(length=4), nullable=False),
        sa.Column("delivery_basis_id", sa.String(length=3), nullable=False),
        sa.Column(
            "delivery_basis_name", sa.String(length=200), nullable=False
        ),
        sa.Column("delivery_type_id", sa.String(length=1), nullable=False),
        sa.Column("volume", sa.Integer(), nullable=False),
        sa.Column("total", sa.Integer(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("date", sa.String(), nullable=False),
        sa.Column("created_on", sa.Date(), nullable=False),
        sa.Column("updated_on", sa.Date(), nullable=False),
        sa.CheckConstraint(
            "count >= 0",
            name=op.f("ck_spimex_trading_results_check_count_positive"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_spimex_trading_results")),
    )


def downgrade() -> None:
    op.drop_table("spimex_trading_results")
