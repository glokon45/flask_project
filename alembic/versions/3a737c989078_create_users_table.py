"""Create users table

Revision ID: 3a737c989078
Revises: 
Create Date: 2021-11-24 13:54:25.750691

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a737c989078'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String),
        sa.Column("password", sa.String))


def downgrade():
    op.drop_table("user")
