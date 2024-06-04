"""New BuyProcess model

Revision ID: 2475a1785a5e
Revises: 2c143b60064f
Create Date: 2023-03-24 19:04:02.902175

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2475a1785a5e"
down_revision = "2c143b60064f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "market_buy_process",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "creation_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("auction_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("seller_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("buyer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["auction_id"],
            ["market_auction.id"],
        ),
        sa.ForeignKeyConstraint(
            ["buyer_id"],
            ["auth_base_user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["seller_id"],
            ["auth_base_user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("market_buy_process")
