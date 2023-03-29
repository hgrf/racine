"""removed unused columns and tables

Revision ID: 31fd4405fcd2
Revises: 70dd6f0306c4
Create Date: 2019-12-15 19:21:54.212347

"""

# revision identifiers, used by Alembic.
revision = "31fd4405fcd2"
down_revision = "70dd6f0306c4"

from alembic import op


def upgrade():
    op.execute(
        """
        CREATE TABLE "samples_new" (
            id INTEGER NOT NULL,
            owner_id INTEGER,
            name VARCHAR(64),
            parent_id INTEGER,
            image VARCHAR(300),
            description TEXT,
            isarchived BOOLEAN,
            isdeleted BOOLEAN,
            last_modified DATETIME,
            PRIMARY KEY (id),
            FOREIGN KEY(owner_id) REFERENCES users (id),
            FOREIGN KEY(parent_id) REFERENCES samples (id)
        );
    """
    )
    op.execute(
        """
        INSERT INTO samples_new (id, owner_id, name, parent_id, image,
                                 description, isarchived, isdeleted, last_modified)
        SELECT id, owner_id, name, parent_id, image,
               description, isarchived, isdeleted, last_modified FROM samples;
    """
    )
    op.execute("DROP TABLE samples;")
    op.execute("ALTER TABLE samples_new RENAME TO samples;")

    op.execute(
        """
        CREATE TABLE "actions_new" (
            id INTEGER NOT NULL,
            timestamp DATE,
            sample_id INTEGER,
            description TEXT,
            owner_id INTEGER,
            datecreated DATE,
            ordnum INTEGER,
            PRIMARY KEY (id),
            CONSTRAINT actions FOREIGN KEY(owner_id) REFERENCES users (id),
            FOREIGN KEY(sample_id) REFERENCES samples (id)
        );
    """
    )
    op.execute(
        """
        INSERT INTO actions_new (id, timestamp, sample_id, description,
                                 owner_id, datecreated, ordnum)
        SELECT id, timestamp, sample_id, description, owner_id, datecreated, ordnum FROM actions;
    """
    )
    op.execute("DROP TABLE actions;")
    op.execute("ALTER TABLE actions_new RENAME TO actions;")

    op.drop_table("sampletypes")
    op.drop_table("actiontypes")


def downgrade():
    pass
