"""Initial schema – create city_analysis table.

Revision ID: 001
Revises: None
Create Date: 2026-06-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "city_analysis",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("city_name", sa.String(), nullable=True, index=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("avg_temperature", sa.Float(), nullable=True),
        sa.Column("risk_category", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index(op.f("ix_city_analysis_id"), "city_analysis", ["id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_city_analysis_id"), table_name="city_analysis")
    op.drop_table("city_analysis")
