"""Add model picture

Revision ID: 28c40ecff675
Revises: 63f78443fa41
Create Date: 2022-09-26 20:39:03.423578

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '28c40ecff675'
down_revision = '63f78443fa41'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pictures',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('path', sa.String(length=350), nullable=False),
    sa.Column('description', sa.String(length=300), nullable=False),
    sa.Column('size', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('description'),
    sa.UniqueConstraint('path')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('pictures')
    # ### end Alembic commands ###