"""add process metadata columns

Revision ID: cb5f5c9371b1
Revises: 5f8c7d9e3b10
Create Date: 2025-09-05 11:45:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb5f5c9371b1'
down_revision = '5f8c7d9e3b10'
branch_labels = None
depends_on = None


def _existing_columns(inspector, table_name):
    return {column['name'] for column in inspector.get_columns(table_name)}


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    table_names = set(inspector.get_table_names())

    if 'evaluation_process_lots' in table_names:
        existing = _existing_columns(inspector, 'evaluation_process_lots')
        with op.batch_alter_table('evaluation_process_lots') as batch:
            if 'process_key' not in existing:
                batch.add_column(sa.Column('process_key', sa.String(length=64), nullable=True))
            if 'process_name' not in existing:
                batch.add_column(sa.Column('process_name', sa.String(length=255), nullable=True))
            if 'process_order_index' not in existing:
                batch.add_column(sa.Column('process_order_index', sa.Integer(), nullable=True))

        existing_indexes = {
            idx['name'] for idx in inspector.get_indexes('evaluation_process_lots')
        }
        index_name = op.f('ix_evaluation_process_lots_eval_id_process_key')
        if index_name not in existing_indexes:
            op.create_index(
                index_name,
                'evaluation_process_lots',
                ['evaluation_id', 'process_key'],
                unique=False,
            )

    if 'evaluation_process_steps' in table_names:
        existing = _existing_columns(inspector, 'evaluation_process_steps')
        with op.batch_alter_table('evaluation_process_steps') as batch:
            if 'process_key' not in existing:
                batch.add_column(sa.Column('process_key', sa.String(length=64), nullable=True))
            if 'process_name' not in existing:
                batch.add_column(sa.Column('process_name', sa.String(length=255), nullable=True))
            if 'process_order_index' not in existing:
                batch.add_column(sa.Column('process_order_index', sa.Integer(), nullable=True))

        existing_indexes = {
            idx['name'] for idx in inspector.get_indexes('evaluation_process_steps')
        }
        index_name = op.f('ix_evaluation_process_steps_eval_id_process_order')
        if index_name not in existing_indexes:
            op.create_index(
                index_name,
                'evaluation_process_steps',
                ['evaluation_id', 'process_order_index'],
                unique=False,
            )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if 'evaluation_process_steps' in inspector.get_table_names():
        existing_indexes = {
            idx['name'] for idx in inspector.get_indexes('evaluation_process_steps')
        }
        index_name = op.f('ix_evaluation_process_steps_eval_id_process_order')
        if index_name in existing_indexes:
            op.drop_index(index_name, table_name='evaluation_process_steps')
        existing = _existing_columns(inspector, 'evaluation_process_steps')
        with op.batch_alter_table('evaluation_process_steps') as batch:
            if 'process_order_index' in existing:
                batch.drop_column('process_order_index')
            if 'process_name' in existing:
                batch.drop_column('process_name')
            if 'process_key' in existing:
                batch.drop_column('process_key')

    if 'evaluation_process_lots' in inspector.get_table_names():
        existing_indexes = {
            idx['name'] for idx in inspector.get_indexes('evaluation_process_lots')
        }
        index_name = op.f('ix_evaluation_process_lots_eval_id_process_key')
        if index_name in existing_indexes:
            op.drop_index(index_name, table_name='evaluation_process_lots')
        existing = _existing_columns(inspector, 'evaluation_process_lots')
        with op.batch_alter_table('evaluation_process_lots') as batch:
            if 'process_order_index' in existing:
                batch.drop_column('process_order_index')
            if 'process_name' in existing:
                batch.drop_column('process_name')
            if 'process_key' in existing:
                batch.drop_column('process_key')
