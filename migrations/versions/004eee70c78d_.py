"""empty message

Revision ID: 004eee70c78d
Revises: 512e1a43a6e8
Create Date: 2024-07-11 12:13:12.241558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004eee70c78d'
down_revision = '512e1a43a6e8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('test_game_resource_log', schema=None) as batch_op:
        batch_op.add_column(sa.Column('source', sa.String(length=64), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('test_game_resource_log', schema=None) as batch_op:
        batch_op.drop_column('source')

    # ### end Alembic commands ###