# Guten Datalake

FastAPI/SQLAlchemy persistence service on port **8005**, serving routes under /guten and connecting to the guten_datalake PostgreSQL database. Models, CRUD, schemas, and routes live under app/.

The live database is the master source for site content. Portal authoring and View Draft use draft data; Guten Sites reads published snapshots. The database baseline in scripts/database/schema.sql must be followed by all numbered migrations for a new database; never rerun the baseline on an existing database.

## Local development

From the sibling coordination repository:

```bash
cd ../guten
make run SERVICE=datalake
make check SERVICE=datalake
make backup
```

Select the existing Guten Python environment through DATALAKE_PYTHON in ignored local.mk. Python requirements are recorded in requirements.in and requirements.txt. PostgreSQL is native/shared on this Mac and is not managed by the launcher.

The application requires `DATABASE_URL` or a file-mounted `DATABASE_URL_FILE`; see `.env.example`. Configure exactly one source. It loads the service’s ignored `.env` without overriding explicitly supplied environment variables. There is no credential fallback. Normal logs go to the console without SQL parameters or content payloads; optional `LOG_FILE` enables bounded rotating logs. The backup tools use standard PostgreSQL PG* connection variables, not SQLAlchemy DATABASE_URL.

## Backup and restore

[scripts/database/backup.sh](scripts/database/backup.sh) exports one consistent full archive and derives separate schema/data SQL files. [scripts/database/restore.sh](scripts/database/restore.sh) restores to a new guten_* database and refuses existing databases and guten_datalake.

Read the [backup/recovery guide](docs/psql/how-to-backup-psql.md). Keep db_dump ignored, copy completed archives to separate storage, and archive frontend image files independently. A Dockerfile now packages the service; database lifecycle remains a separate Compose project.

See [local operations](../guten/README.md) and [storage and Git conventions](../guten/docs/storage-and-git.md). Other documents in docs are historical references and may describe unfinished features.

## Project structure

```text
app/ — models, request/response schemas, CRUD, FastAPI routes
scripts/database/ — baseline, migrations, migration runner, backup/restore
tests/ — guarded PostgreSQL/FastAPI/Crust integration tests
docs/ — operational and API notes
```

See [scoped names, ordering, and migrations](docs/scoping-and-ordering.md) for the current contract.

See [editorial references and notes](docs/editorial-refs-and-notes.md) for the Portal CRUD API and validation rules.

See [per-site publishing](docs/publishing.md) for the editor workflow, API, migration, and initial publication seeding. Portal/View Draft reads draft; Guten Sites reads published content only.

`/health/live` checks the process; `/health/ready` checks database connectivity and exact migration checksums, returning 503 when not ready. Neither endpoint migrates the database. See the [repeatable acceptance guide](../guten/docs/testing.md) for empty-database setup and retained reports.

## Containers

The Dockerfile and .dockerignore package this service without local secrets, dumps, installed dependencies or content media. Build/start it using the sibling coordination repository’s [Docker Compose guide](../guten/docs/docker.md). The container rehearsal uses a separate empty database and alternate localhost ports.
