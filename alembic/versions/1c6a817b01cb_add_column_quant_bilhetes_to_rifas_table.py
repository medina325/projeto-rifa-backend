"""add column quant_bilhetes to rifas table

Revision ID: 1c6a817b01cb
Revises: a40a3872892e
Create Date: 2024-07-05 09:50:51.159439

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c6a817b01cb'
down_revision: Union[str, None] = 'a40a3872892e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('rifas', sa.Column('quant_bilhetes', sa.Integer(), nullable=False))


def downgrade() -> None:
    op.drop_column('rifas', 'quant_bilhetes')
