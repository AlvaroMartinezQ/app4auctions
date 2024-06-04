"""New celery objects in db

Revision ID: 2c143b60064f
Revises: a5c1edb0299f
Create Date: 2023-03-20 19:12:33.346222

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2c143b60064f"
down_revision = "a5c1edb0299f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "celery_task",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("task_type", sa.String(length=30), nullable=False),
        sa.Column("task_uuid", sa.String(length=50), nullable=False),
        sa.Column("auction_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["auction_id"],
            ["market_auction.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("task_uuid"),
    )
    op.drop_column("market_auction", "celery_id")


def downgrade() -> None:
    op.add_column(
        "market_auction",
        sa.Column("celery_id", postgresql.UUID(), autoincrement=False, nullable=True),
    )
    op.drop_table("celery_task")
    # ### end Alembic commands ###
