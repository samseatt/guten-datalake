# Guten database archives and recovery

The live `guten_datalake` database is the master content source. Never recreate it from the historical `scripts/database/schema.sql`. Archive the live database before schema changes.

## Backup

From the guten-datalake repository:

```bash
bash scripts/database/backup.sh
# Or place a new archive in another existing/writable storage location:
bash scripts/database/backup.sh /path/to/archive-parent
```

The source database is deliberately fixed to `guten_datalake`. The default output is an ignored `db_dump/guten_datalake_<UTC timestamp>_<unique suffix>/` directory. No archive is overwritten or automatically deleted. Files are private to the local user.

Each archive contains:

- `full.dump`: the authoritative PostgreSQL custom-format backup, including schema, data, constraints, indexes, and sequence values.
- `schema.sql`: a readable schema export derived from that same archive.
- `data.sql`: a readable data export derived from that same archive.
- `archive-toc.txt`: archive inventory.
- `metadata.txt`: source PostgreSQL version, database encoding, locale, and archive creation time.
- `SHA256SUMS`: checksums for the files above.

A failed run retains its folder with an `INCOMPLETE` marker. Do not use it for recovery. The restore script rejects it. The script accesses the source in read-only mode; PostgreSQL's dump provides a consistent snapshot while content editing can continue. Sequence counters can advance independently of table snapshots, which can create harmless ID gaps.

Copy the whole completed archive directory to separate storage and verify its checksums there. A copy on the same Mac does not protect against loss of the Mac. These archives contain the actual content and must not be committed to Git. There is no automatic schedule or retention policy yet.

## Restore safely

Use a trusted archive and a NEW database name:

```bash
bash scripts/database/restore.sh /absolute/path/to/archive guten_restore_20260916
```

The script checks file integrity, creates a database from `template0`, and restores the full archive in one transaction. It refuses `guten_datalake`, names outside `guten_*`, and every existing target database. It never uses `--clean`, drops a database, or changes an application connection. A failed restore leaves the new database for inspection; retry with a new name after resolving the failure.

After restoration, verify table counts, representative content and relations, constraints, and sequence values. Run the application against the recovery database before deliberately switching away from the original. Recovery does not require overwriting the original database. Do not import `schema.sql` and `data.sql` sequentially as the normal restore procedure: the full archive allows `pg_restore` to order data and constraint restoration correctly.

## Connection settings and portability

Requirements: Bash, PostgreSQL client tools (`pg_dump`, `pg_restore`, `psql`, `createdb`), and `shasum`. Use matching dump/restore client tools; the dump client must support the source server. Restoring to older PostgreSQL major versions is not a supported migration plan.

Both scripts honor standard libpq variables: `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSFILE`, and `PGSSLMODE`. They do not read the application's SQLAlchemy `DATABASE_URL` or load `.env`. Use a password file with permissions `0600`; do not put passwords in scripts or Git. `-w` makes a missing credential fail rather than hang unattended.

For a future RDS restore, set these variables to the target connection, using appropriate TLS verification and a role allowed to create a new database. Check target extensions, encoding, and locale against `metadata.txt` before migration. This helper uses the target template0's encoding/locale defaults; locale differences require a deliberate migration decision. A full AWS migration rehearsal remains necessary.

The full archive preserves source ownership/privilege metadata, but the restore helper skips original owners, grants, and tablespaces for portability. Objects belong to the restoring role; application access must be configured explicitly on the target. Cluster-wide roles/passwords and server configuration are not included in a per-database dump.

## Media is separate

Database backups preserve image URLs/paths, not image files in the frontend `public/assets` directories or remote storage. Keep the archived repositories/assets alongside the database archive for complete site recovery.
