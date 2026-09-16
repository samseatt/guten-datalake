#!/bin/bash
# Restore a trusted archive into a NEW database. Never drops or cleans databases.
set -euo pipefail
export LC_ALL=C
if [[ ${1:-} == --help ]]; then
  echo "Usage: $0 ARCHIVE_DIRECTORY NEW_GUTEN_DATABASE_NAME"
  echo "Example target: guten_restore_20260916. Existing databases and guten_datalake are refused."
  echo "Connection: PGHOST, PGPORT, PGUSER, PGPASSFILE, PGSSLMODE."
  exit 0
fi
if [[ $# -ne 2 ]]; then
  echo "Usage: $0 ARCHIVE_DIRECTORY NEW_GUTEN_DATABASE_NAME" >&2
  exit 2
fi
archive_dir=$(cd -- "$1" && pwd)
target_db=$2
if [[ ! $target_db =~ ^guten_[a-z0-9_]+$ || ${#target_db} -gt 63 || $target_db == guten_datalake ]]; then
  echo 'Target must be a new guten_* database (lowercase letters/digits/underscores, <=63 characters), never guten_datalake.' >&2
  exit 2
fi
for tool in pg_restore createdb shasum; do
  command -v "$tool" >/dev/null || { echo "Missing required tool: $tool" >&2; exit 1; }
done
if [[ -e "$archive_dir/INCOMPLETE" || ! -s "$archive_dir/full.dump" || ! -s "$archive_dir/SHA256SUMS" ]]; then
  echo 'Missing or incomplete archive.' >&2
  exit 1
fi
# Require an explicit checksum for the file that will be restored.
if ! grep -Eq '^[0-9a-f]{64}  full\.dump$' "$archive_dir/SHA256SUMS"; then
  echo 'Missing full.dump checksum.' >&2
  exit 1
fi
(cd -- "$archive_dir" && shasum -a 256 -c SHA256SUMS)
pg_restore --list "$archive_dir/full.dump" >/dev/null
# createdb is the race-safe existing-database guard. If it fails, do not restore.
createdb -w --maintenance-db=postgres --template=template0 -- "$target_db"
trap 'echo "Restore failed; target database $target_db retained for inspection. Source database untouched." >&2' ERR
# Portable ownership: new objects belong to the restoring role. Configure grants separately.
pg_restore -w --exit-on-error --single-transaction --no-owner --no-privileges --no-tablespaces \
  --dbname="$target_db" "$archive_dir/full.dump"
trap - ERR
printf 'Restored successfully into: %s\n' "$target_db"
echo 'Application connections have not been changed. Validate content and target configuration before switching.'
