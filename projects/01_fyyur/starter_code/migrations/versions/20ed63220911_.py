"""empty message

Revision ID: 20ed63220911
Revises: 2ad7b0e10d54
Create Date: 2020-10-19 22:28:02.545882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20ed63220911'
down_revision = '2ad7b0e10d54'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('Artist_id', sa.Integer(), nullable=False))
    op.add_column('shows', sa.Column('Venue_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'shows', 'Venue', ['Venue_id'], ['id'])
    op.create_foreign_key(None, 'shows', 'Artist', ['Artist_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'shows', type_='foreignkey')
    op.drop_constraint(None, 'shows', type_='foreignkey')
    op.drop_column('shows', 'Venue_id')
    op.drop_column('shows', 'Artist_id')
    # ### end Alembic commands ###