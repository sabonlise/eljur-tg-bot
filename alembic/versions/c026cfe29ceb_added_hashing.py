"""added hashing

Revision ID: c026cfe29ceb
Revises: 
Create Date: 2020-05-05 23:23:15.695066

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c026cfe29ceb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('hash', sa.String(), nullable=True))
    op.drop_column('users', 'chat_hash')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('chat_hash', sa.VARCHAR(), nullable=True))
    op.drop_column('users', 'hash')
    # ### end Alembic commands ###
