"""empty message

Revision ID: 070ae05cf5bb
Revises: df54d0cc5d66
Create Date: 2024-07-15 19:54:53.482987

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '070ae05cf5bb'
down_revision = 'df54d0cc5d66'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('test_game', schema=None) as batch_op:
        batch_op.alter_column('cash',
               existing_type=sa.FLOAT(),
               type_=sa.Integer(),
               existing_nullable=True)

    with op.batch_alter_table('test_game_building_progress', schema=None) as batch_op:
        batch_op.alter_column('cash_per_minute',
               existing_type=sa.FLOAT(),
               type_=sa.Integer(),
               existing_nullable=True)
        batch_op.alter_column('accrued_cash',
               existing_type=sa.FLOAT(),
               type_=sa.Integer(),
               existing_nullable=True)

    with op.batch_alter_table('test_game_buildings', schema=None) as batch_op:
        batch_op.alter_column('base_cash_per_minute',
               existing_type=sa.FLOAT(),
               type_=sa.Integer(),
               existing_nullable=True)

    with op.batch_alter_table('test_game_items', schema=None) as batch_op:
        batch_op.alter_column('item_cost',
               existing_type=sa.FLOAT(),
               type_=sa.Integer(),
               existing_nullable=True)

    with op.batch_alter_table('test_game_resource_log', schema=None) as batch_op:
        batch_op.alter_column('cash',
               existing_type=sa.FLOAT(),
               type_=sa.Integer(),
               existing_nullable=True)

    with op.batch_alter_table('test_game_rewards', schema=None) as batch_op:
        batch_op.alter_column('quest_reward_cash',
               existing_type=sa.FLOAT(),
               type_=sa.Integer(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('test_game_rewards', schema=None) as batch_op:
        batch_op.alter_column('quest_reward_cash',
               existing_type=sa.Integer(),
               type_=sa.FLOAT(),
               existing_nullable=True)

    with op.batch_alter_table('test_game_resource_log', schema=None) as batch_op:
        batch_op.alter_column('cash',
               existing_type=sa.Integer(),
               type_=sa.FLOAT(),
               existing_nullable=True)

    with op.batch_alter_table('test_game_items', schema=None) as batch_op:
        batch_op.alter_column('item_cost',
               existing_type=sa.Integer(),
               type_=sa.FLOAT(),
               existing_nullable=True)

    with op.batch_alter_table('test_game_buildings', schema=None) as batch_op:
        batch_op.alter_column('base_cash_per_minute',
               existing_type=sa.Integer(),
               type_=sa.FLOAT(),
               existing_nullable=True)

    with op.batch_alter_table('test_game_building_progress', schema=None) as batch_op:
        batch_op.alter_column('accrued_cash',
               existing_type=sa.Integer(),
               type_=sa.FLOAT(),
               existing_nullable=True)
        batch_op.alter_column('cash_per_minute',
               existing_type=sa.Integer(),
               type_=sa.FLOAT(),
               existing_nullable=True)

    with op.batch_alter_table('test_game', schema=None) as batch_op:
        batch_op.alter_column('cash',
               existing_type=sa.Integer(),
               type_=sa.FLOAT(),
               existing_nullable=True)

    # ### end Alembic commands ###
