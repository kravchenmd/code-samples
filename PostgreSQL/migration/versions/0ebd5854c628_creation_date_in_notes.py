"""creation date in notes

Revision ID: 0ebd5854c628
Revises: 4cb592d4ddc6
Create Date: 2022-09-18 12:59:19.724185

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ebd5854c628'
down_revision = '4cb592d4ddc6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notes', sa.Column('creation_date', sa.Date(), nullable=True))
    op.drop_column('notes', 'execution_date')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notes', sa.Column('execution_date', sa.DATE(), autoincrement=False, nullable=True))
    op.drop_column('notes', 'creation_date')
    # ### end Alembic commands ###