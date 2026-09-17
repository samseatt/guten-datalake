"""Explicit, one-time initialization of a NEW Compose rehearsal database only."""
import os
from pathlib import Path
from contextlib import closing
import psycopg2
from psycopg2 import sql
from sqlalchemy.engine import make_url
from bootstrap_test_db import create, validate

url = make_url(Path("/run/secrets/database_url").read_text().strip())
validate(url.database)
if url.host != "postgres" or url.username != "guten_app":
    raise RuntimeError("This initializer only accepts the isolated Compose postgres/guten_app rehearsal target.")
os.environ.update(PGHOST="postgres", PGPORT="5432", PGUSER="postgres",
                  PGPASSWORD=Path("/run/secrets/postgres_password").read_text().strip())
create(url.database)  # Refuses any existing database; no automatic reset or migration at app startup.
with closing(psycopg2.connect(dbname=url.database)) as connection, connection:
    with connection.cursor() as cursor:
        cursor.execute("CREATE ROLE guten_app LOGIN PASSWORD %s NOSUPERUSER NOCREATEDB NOCREATEROLE", (url.password,))
        cursor.execute(sql.SQL("GRANT CONNECT ON DATABASE {} TO guten_app").format(sql.Identifier(url.database)))
        for schema in ("draft", "published", "workflow"):
            cursor.execute(sql.SQL("GRANT USAGE ON SCHEMA {} TO guten_app").format(sql.Identifier(schema)))
            cursor.execute(sql.SQL("GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA {} TO guten_app").format(sql.Identifier(schema)))
            cursor.execute(sql.SQL("GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA {} TO guten_app").format(sql.Identifier(schema)))
print("Empty rehearsal database initialized; application role cannot create databases or roles.")
