"""Enable pgvector.

Revision ID: ec1005e02a7a
Revises: 86bcda727b2f
Create Date: 2025-10-18 11:30:56.028642

"""

from typing import Sequence, Union

# import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'ec1005e02a7a'
down_revision: Union[str, Sequence[str], None] = '86bcda727b2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DROP EXTENSION IF EXISTS vector')
