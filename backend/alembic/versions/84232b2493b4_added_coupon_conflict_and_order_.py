"""Added coupon conflict and order relationships

Revision ID: 84232b2493b4
Revises: 637ac11e30dc
Create Date: 2025-01-09 20:48:02.950535

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84232b2493b4'
down_revision: Union[str, None] = '637ac11e30dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
