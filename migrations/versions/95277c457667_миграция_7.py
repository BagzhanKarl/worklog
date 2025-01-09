"""Миграция 7

Revision ID: 95277c457667
Revises: 66487928f2da
Create Date: 2025-01-07 19:19:01.617981

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '95277c457667'
down_revision = '66487928f2da'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vaxta', schema=None) as batch_op:
        batch_op.add_column(sa.Column('iter', sa.Boolean(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vaxta', schema=None) as batch_op:
        batch_op.drop_column('iter')

    # ### end Alembic commands ###
