"""repair broken heir column for sqlite

Revision ID: 362505d00f1a
Revises: 5ae6e19e0a7b
Create Date: 2016-07-04 19:10:36.775432

"""

# revision identifiers, used by Alembic.
revision = "362505d00f1a"
down_revision = "5ae6e19e0a7b"

from alembic import op
import sqlalchemy as sa  # noqa: F401


def upgrade():
    op.execute("DROP INDEX ix_users_email;")
    op.execute("DROP INDEX ix_users_username;")
    op.execute(
        """
        CREATE TABLE "users_new" (
            id INTEGER NOT NULL,
            email VARCHAR(64),
            username VARCHAR(64),
            password_hash VARCHAR(128),
            is_admin BOOLEAN,
            heir_id INTEGER,
            PRIMARY KEY (id),
            CHECK (is_admin IN (0, 1)),
            CONSTRAINT users_new FOREIGN KEY(heir_id) REFERENCES users (id)
        );"""
    )
    op.execute(
        """
        INSERT INTO users_new (id, email, username, password_hash, is_admin, heir_id)
          SELECT id, email, username, password_hash, is_admin, heir_id FROM users;
    """
    )
    op.execute("DROP TABLE users;")
    op.execute("ALTER TABLE users_new RENAME TO users;")
    op.execute("CREATE UNIQUE INDEX ix_users_email ON users (email);")
    op.execute("CREATE UNIQUE INDEX ix_users_username ON users (username);")


def downgrade():
    pass
