"""add mountpoint column

Revision ID: 506bb8a29f4d
Revises: 3d9e4225ecbd
Create Date: 2019-08-01 18:55:44.112031

"""

# revision identifiers, used by Alembic.
revision = "506bb8a29f4d"
down_revision = "3d9e4225ecbd"

from alembic import op
import sqlalchemy as sa  # noqa: F401


def upgrade():
    op.execute(
        """
        CREATE TABLE shares_new (
            id INTEGER NOT NULL,
            sample_id INTEGER,
            user_id INTEGER,
            mountpoint_id INTEGER,
            PRIMARY KEY (id),
            FOREIGN KEY(sample_id) REFERENCES samples (id),
            FOREIGN KEY(user_id) REFERENCES users (id),
            FOREIGN KEY(mountpoint_id) REFERENCES samples (id)
    );"""
    )
    op.execute(
        "INSERT INTO shares_new (id, sample_id, user_id) SELECT id, sample_id, user_id FROM shares;"
    )
    op.execute("UPDATE shares_new SET mountpoint_id=0;")
    op.execute("DROP TABLE shares;")
    op.execute("ALTER TABLE shares_new RENAME TO shares;")


def downgrade():
    pass
