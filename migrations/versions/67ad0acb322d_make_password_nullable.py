"""Make password nullable

Revision ID: 67ad0acb322d
Revises: 7bd8f145c14d
Create Date: 2024-11-19 16:43:27.981200

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '67ad0acb322d'
down_revision: Union[str, None] = '7bd8f145c14d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column('users', 'password', nullable=True)


def downgrade():
    pass
