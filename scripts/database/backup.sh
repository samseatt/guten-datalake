#!/bin/bash
# Back up only guten_datalake; standard libpq PG* variables select the server.
set -euo pipefail
export LC_ALL=C
umask 077
if [[ $# -gt 1 || ${1:-} == --help ]]; then
  echo "Usage: $0 [archive-parent-directory]"
  echo "Connection: PGHOST, PGPORT, PGUSER, PGPASSFILE, PGSSLMODE. Source: guten_datalake."
  exit 0
fi
for tool in pg_dump pg_restore psql shasum; do
  command -v "$tool" >/dev/null || { echo "Missing required tool: $tool" >&2; exit 1; }
done
script_dir=$(cd -- "$(dirname -- "$0")" && pwd)
archive_parent=${1:-"$script_dir/../../db_dump"}
mkdir -p -- "$archive_parent"
archive_parent=$(cd -- "$archive_parent" && pwd)
archive_dir=$(mktemp -d "$archive_parent/guten_datalake_$(date -u +%Y%m%dT%H%M%SZ)_XXXXXX")
touch "$archive_dir/INCOMPLETE"
trap 'echo "Backup failed; incomplete files retained at: $archive_dir" >&2' ERR
export PGOPTIONS="${PGOPTIONS:-} -c default_transaction_read_only=on"
{
  printf 'Archive created UTC: %s\nSource database: guten_datalake\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  pg_dump --version
  psql -X -w -d guten_datalake -At -v ON_ERROR_STOP=1 -c "SELECT 'Server: ' || version();"
  psql -X -w -d guten_datalake -At -v ON_ERROR_STOP=1 -c "SELECT 'Encoding: ' || pg_encoding_to_char(encoding) || E'\nLC_COLLATE: ' || datcollate || E'\nLC_CTYPE: ' || datctype FROM pg_database WHERE datname = current_database();"
} > "$archive_dir/metadata.txt"
# One snapshot. Derive both SQL exports from this archive, not separate live dumps.
pg_dump -w --format=custom --lock-wait-timeout=30s --dbname=guten_datalake --file="$archive_dir/full.dump"
pg_restore --schema-only --file="$archive_dir/schema.sql" "$archive_dir/full.dump"
pg_restore --data-only --file="$archive_dir/data.sql" "$archive_dir/full.dump"
pg_restore --list "$archive_dir/full.dump" > "$archive_dir/archive-toc.txt"
(cd -- "$archive_dir" && shasum -a 256 full.dump schema.sql data.sql archive-toc.txt metadata.txt > SHA256SUMS && shasum -a 256 -c SHA256SUMS)
rm -- "$archive_dir/INCOMPLETE"
trap - ERR
printf 'Backup complete: %s\n' "$archive_dir"
echo 'Archive integrity checked. A successful restore rehearsal is still needed to verify recoverability.'
