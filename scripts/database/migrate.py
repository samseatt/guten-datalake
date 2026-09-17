#!/usr/bin/env python3
"""Apply checksummed SQL migrations atomically using standard PostgreSQL PG* settings."""
import argparse
import hashlib
from pathlib import Path
import psycopg2


def migrate(database, allow_master=False):
    if not database.startswith("guten_") or (database == "guten_datalake" and not allow_master):
        raise ValueError("Use a Guten rehearsal database; master requires --allow-master after backup/rehearsal.")
    files = sorted((Path(__file__).parent / "migrations").glob("*.sql"))
    with psycopg2.connect(dbname=database) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL lock_timeout = '5s'")
            cursor.execute("SET LOCAL statement_timeout = '60s'")
            cursor.execute("SELECT pg_advisory_xact_lock(718264019)")
            cursor.execute("""CREATE TABLE IF NOT EXISTS workflow.schema_migrations (
                version text PRIMARY KEY, sha256 text NOT NULL,
                applied_at timestamptz NOT NULL DEFAULT now())""")
            cursor.execute("SELECT version, sha256 FROM workflow.schema_migrations")
            applied = dict(cursor.fetchall())
            if set(applied) - {p.name for p in files}:
                raise ValueError("Database contains migrations absent from this checkout.")
            for path in files:
                data = path.read_bytes()
                digest = hashlib.sha256(data).hexdigest()
                if path.name in applied:
                    if applied[path.name] != digest:
                        raise ValueError(f"Applied migration changed: {path.name}")
                    print(f"Already applied: {path.name}")
                    continue
                cursor.execute(data.decode())
                cursor.execute("INSERT INTO workflow.schema_migrations (version, sha256) VALUES (%s,%s)", (path.name,digest))
                print(f"Applying: {path.name}")
    print(f"Migration transaction committed: {database}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True)
    parser.add_argument("--allow-master", action="store_true")
    args = parser.parse_args()
    migrate(args.database, args.allow_master)
