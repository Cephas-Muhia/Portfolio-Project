"""Add date_lost column to lost_item table

Revision ID: 067a381ee387
Revises: 8b09b0588336
Create Date: 2024-07-21 14:38:54.828969

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '067a381ee387'
down_revision = '8b09b0588336'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('lost_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_lost', sa.DateTime(), nullable=False, server_default=sa.func.now()))

    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('lost_item', schema=None) as batch_op:
        batch_op.drop_column('date_lost')

    # ### end Alembic commands ###
