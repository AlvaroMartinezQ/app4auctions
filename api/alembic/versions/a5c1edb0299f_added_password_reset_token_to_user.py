"""Added password reset token to user

Revision ID: a5c1edb0299f
Revises: 4e84803b6061
Create Date: 2023-03-05 16:52:34.386810

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a5c1edb0299f"
down_revision = "4e84803b6061"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "auth_base_user",
        sa.Column("pwd_reset_token", sa.String(length=10), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("auth_base_user", "pwd_reset_token")
