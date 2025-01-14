"""Ворклог 2

Revision ID: 0fc88017ba29
Revises: 53ab69483e8c
Create Date: 2025-01-11 14:43:14.503659

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0fc88017ba29'
down_revision = '53ab69483e8c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('page', sa.String(length=50), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('permissions', schema=None) as batch_op:
        batch_op.drop_column('page')

    # ### end Alembic commands ###
