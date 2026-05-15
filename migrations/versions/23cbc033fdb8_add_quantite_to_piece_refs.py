"""add quantite to piece_refs

Revision ID: 23cbc033fdb8
Revises: b6ceb7c90097
Create Date: 2026-05-15 09:25:33.102041

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23cbc033fdb8'
down_revision = 'b6ceb7c90097'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('piece_refs',
        sa.Column('quantite', sa.Integer(), nullable=False, server_default='0')
    )

def downgrade():
    op.drop_column('piece_refs', 'quantite')
