"""Remove unique constraint from sample name

Revision ID: 3d9e4225ecbd
Revises: 362505d00f1a
Create Date: 2016-07-04 19:25:25.851804

"""

# revision identifiers, used by Alembic.
revision = "3d9e4225ecbd"
down_revision = "362505d00f1a"

from alembic import op
import sqlalchemy as sa  # noqa: F401


def upgrade():
    op.execute("DROP INDEX ix_samples_name;")
    op.execute(
        """
        CREATE TABLE samples_new (
            id INTEGER NOT NULL,
            owner_id INTEGER,
            name VARCHAR(64),
            parent_id INTEGER,
            sampletype_id INTEGER,
            image VARCHAR(300),
            mwidth INTEGER,
            mheight INTEGER,
            mx INTEGER,
            my INTEGER, description TEXT, isarchived BOOLEAN,
            PRIMARY KEY (id),
            FOREIGN KEY(owner_id) REFERENCES users (id),
            FOREIGN KEY(parent_id) REFERENCES samples (id),
            FOREIGN KEY(sampletype_id) REFERENCES sampletypes (id)
        );"""
    )
    op.execute(
        """
        INSERT INTO samples_new (id, owner_id, name, parent_id, sampletype_id,
                                 image, mwidth, mheight, mx, my, description, isarchived)
        SELECT id, owner_id, name, parent_id, sampletype_id,
               image, mwidth, mheight, mx, my, description, isarchived FROM samples;
    """
    )
    op.execute("DROP TABLE samples;")
    op.execute("ALTER TABLE samples_new RENAME TO samples;")


def downgrade():
    pass
