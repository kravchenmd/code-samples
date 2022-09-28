"""phone email nullable

Revision ID: 4cb592d4ddc6
Revises: 2230a36b1717
Create Date: 2022-09-17 11:50:44.449747

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4cb592d4ddc6'
down_revision = '2230a36b1717'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('contact_details', 'phone_list',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=True)
    op.alter_column('contact_details', 'email_list',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('contact_details', 'email_list',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=False)
    op.alter_column('contact_details', 'phone_list',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               nullable=False)
    # ### end Alembic commands ###