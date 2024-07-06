"""empty message

Revision ID: ffc702d50562
Revises: ef580d5fcf6b
Create Date: 2024-07-06 13:03:47.134272

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ffc702d50562'
down_revision = 'ef580d5fcf6b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('test_game_inventory_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('inventory_type_name', sa.String(length=64), nullable=True),
    sa.Column('inventory_type_description', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('test_game_inventory', schema=None) as batch_op:
        batch_op.add_column(sa.Column('type', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'test_game_inventory_types', ['type'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('test_game_inventory', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('type')

    op.drop_table('test_game_inventory_types')
    # ### end Alembic commands ###
