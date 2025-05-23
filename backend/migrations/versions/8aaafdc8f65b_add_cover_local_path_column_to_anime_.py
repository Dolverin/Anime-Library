"""Add cover_local_path column to Anime model

Revision ID: 8aaafdc8f65b
Revises: b33652bde440
Create Date: 2025-05-03 19:54:27.232082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8aaafdc8f65b'
down_revision: Union[str, None] = 'b33652bde440'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('animes', sa.Column('cover_local_path', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('animes', 'cover_local_path')
    # ### end Alembic commands ###
