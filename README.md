# Guten Datalake

FastAPI/SQLAlchemy persistence service on port **8005**, serving routes under /guten and connecting to the guten_datalake PostgreSQL database. Models, CRUD, schemas, and routes live under app/.

The live database is the master source for site content. Both authoring and public rendering currently use draft data intentionally. The published schema/workflow exist but publishing is incomplete. The historical scripts/database/schema.sql differs from the live database and must not be used to recreate it blindly.

## Local development

From the sibling coordination repository:

```bash
cd ../guten
make run SERVICE=datalake
make check SERVICE=datalake
make backup
```

Select the existing Guten Python environment through DATALAKE_PYTHON in ignored local.mk. Python requirements are recorded in requirements.in and requirements.txt. PostgreSQL is native/shared on this Mac and is not managed by the launcher.

The application reads DATABASE_URL, with a legacy hard-coded fallback in app/database.py. The current local .env is empty; configuration cleanup remains pending. The backup tools use standard PostgreSQL PG* connection variables, not SQLAlchemy DATABASE_URL.

## Backup and restore

[scripts/database/backup.sh](scripts/database/backup.sh) exports one consistent full archive and derives separate schema/data SQL files. [scripts/database/restore.sh](scripts/database/restore.sh) restores to a new guten_* database and refuses existing databases and guten_datalake.

Read the [backup/recovery guide](docs/psql/how-to-backup-psql.md). Keep db_dump ignored, copy completed archives to separate storage, and archive frontend image files independently. No working Docker setup is supplied yet; the empty historical Dockerfile has been removed.

See [local operations](../guten/README.md) and [storage and Git conventions](../guten/docs/storage-and-git.md). Other documents in docs are historical references and may describe unfinished features.

## Project structure

```text
app/ — models, request/response schemas, CRUD, FastAPI routes
scripts/database/ — baseline, migrations, migration runner, backup/restore
tests/ — guarded PostgreSQL/FastAPI/Crust integration tests
docs/ — operational and API notes
```

See [scoped names, ordering, and migrations](docs/scoping-and-ordering.md) for the current contract.
