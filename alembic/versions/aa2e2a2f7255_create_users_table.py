"""create users table

Revision ID: aa2e2a2f7255
Revises: 
Create Date: 2024-06-16 14:53:53.675168

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa2e2a2f7255'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.String(30), primary_key=True),
        sa.Column('username', sa.String(255), unique=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255)),
        sa.Column('first_name', sa.String(255), nullable=False),
        sa.Column('last_name', sa.String(255), nullable=False),
        sa.Column('picture', sa.String(255)),
        sa.Column('auth_provider', sa.String(50)),
        sa.Column(
            'created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()
        ),
        sa.Column(
            'updated_at',
            sa.TIMESTAMP,
            server_default=sa.func.current_timestamp(),
            onupdate=sa.func.current_timestamp(),
        ),
    )


def downgrade() -> None:
    op.drop_table('users')
