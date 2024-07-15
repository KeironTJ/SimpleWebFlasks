"""empty message

Revision ID: 67eb132d7754
Revises: cfb0333442b5
Create Date: 2024-07-15 08:35:33.765882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67eb132d7754'
down_revision = 'cfb0333442b5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('test_game_level_requirements')
    with op.batch_alter_table('test_game_building_progress', schema=None) as batch_op:
        batch_op.add_column(sa.Column('base_building_xp_required', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('base_building_wood_required', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('base_building_stone_required', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('base_building_metal_required', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('test_game_building_progress', schema=None) as batch_op:
        batch_op.drop_column('base_building_metal_required')
        batch_op.drop_column('base_building_stone_required')
        batch_op.drop_column('base_building_wood_required')
        batch_op.drop_column('base_building_xp_required')

    op.create_table('test_game_level_requirements',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('level', sa.INTEGER(), nullable=True),
    sa.Column('xp_required', sa.INTEGER(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
