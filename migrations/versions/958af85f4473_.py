"""empty message

Revision ID: 958af85f4473
Revises: 629c39cd7fe4
Create Date: 2024-07-01 12:26:29.049681

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '958af85f4473'
down_revision = '629c39cd7fe4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('active', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('active')

    # ### end Alembic commands ###