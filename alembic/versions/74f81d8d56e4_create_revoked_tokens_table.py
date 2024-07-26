"""create revoked_tokens table

Revision ID: 74f81d8d56e4
Revises: aa2e2a2f7255
Create Date: 2024-06-16 14:56:32.516793

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74f81d8d56e4'
down_revision: Union[str, None] = 'aa2e2a2f7255'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'revoked_tokens',
        sa.Column('token', sa.String, primary_key=True, index=True),
        sa.Column(
            'revoked_at', sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )


def downgrade() -> None:
    op.drop_table('revoked_tokens')
