"""Ворклог 5

Revision ID: dd00aa9f89fb
Revises: f466e0954bcf
Create Date: 2025-01-14 12:26:26.384053

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd00aa9f89fb'
down_revision = 'f466e0954bcf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('report_shift',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('from_on', sa.String(length=12), nullable=False),
    sa.Column('to', sa.String(length=12), nullable=False),
    sa.Column('created_by', sa.Integer(), nullable=False),
    sa.Column('can_see', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['can_see'], ['users.id'], ),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('report_shift')
    # ### end Alembic commands ###
