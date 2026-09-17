"""Create a NEW synthetic test database from the committed baseline and migrations."""
import argparse
from contextlib import closing
import re
from pathlib import Path
import psycopg2
from psycopg2 import sql
from migrate import migrate


def validate(database):
    if len(database) > 63 or not re.fullmatch(r"guten_[a-z0-9]+_test_[a-z0-9_]+", database):
        raise ValueError("Expected a disposable database named guten_<purpose>_test_<suffix>.")


def create(database):
    validate(database)
    connection = psycopg2.connect(dbname="postgres")
    connection.autocommit = True
    try:
        with connection.cursor() as cursor:
            # CREATE fails if it exists: never reuse, overwrite or remove existing databases.
            cursor.execute(sql.SQL("CREATE DATABASE {} TEMPLATE template0").format(sql.Identifier(database)))
    finally:
        connection.close()
    try:
        with closing(psycopg2.connect(dbname=database)) as connection, connection:
            with connection.cursor() as cursor:
                cursor.execute((Path(__file__).parent / "schema.sql").read_text())
        migrate(database)
    except BaseException:
        drop(database)
        raise


def drop(database):
    validate(database)
    connection = psycopg2.connect(dbname="postgres")
    connection.autocommit = True
    try:
        with connection.cursor() as cursor:
            # Call only for a database successfully created by this invocation.
            cursor.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(database)))
    finally:
        connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True)
    create(parser.parse_args().database)
