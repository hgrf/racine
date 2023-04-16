"""Adds serverport and domain to SMBResource

Revision ID: e5dcaf21bbf0
Revises: 71c1f7625171
Create Date: 2023-04-16 15:02:33.373396

"""

# revision identifiers, used by Alembic.
revision = 'e5dcaf21bbf0'
down_revision = '71c1f7625171'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('smbresources', schema=None) as batch_op:
        batch_op.add_column(sa.Column('serverport', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('domainname', sa.String(length=64), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('smbresources', schema=None) as batch_op:
        batch_op.drop_column('domainname')
        batch_op.drop_column('serverport')

    # ### end Alembic commands ###