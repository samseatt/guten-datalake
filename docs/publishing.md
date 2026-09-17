# Per-site publication

## Editor workflow

Portal edits and View Draft always read draft. Guten Sites reads published content only, never falling back to draft. Dashboard cards show Not published, Unpublished changes, or Published, plus the last successful publish time. Refresh publication status after editing in another tab. Publish fetches fresh status and asks for confirmation; the request includes the reviewed draft fingerprint. A changed draft returns 409 rather than publishing unreviewed edits.

Publish synchronizes one site's metadata, sections, pages, editorial references, and editorial notes. Stable IDs, scoped names, order, landing selections, image paths, tags, and timestamps are retained. Refs/Notes remain absent from rendered pages. An unchanged publish is a no-op that preserves its timestamp and publication count. Deletions and renames stay draft-only until the next Publish.

Unpublish removes the public copy and retains the draft and publication history. It checks the reviewed published fingerprint so a newer publication cannot silently be removed. A published site cannot be deleted through draft site deletion until it is explicitly unpublished. A site with no pages can be published, but its landing URL reports that no published page is available.

Template and theme assignments are not implemented by the current renderer. Current content has no such assignments. Publish rejects non-null page template or section-theme assignments rather than copying a shared mutable dependency into supposedly isolated publications. Existing active site color/logo fields are supported. Media files are not copied: publication preserves their paths, so replacing an image at the same path also affects an already published page.

## Transactions and consistency

All application content mutations and publication commands lock the draft site row. A single SQL statement captures complete draft and published snapshots; writes use that captured draft payload, rather than rereading individual draft tables. Publishing deletes obsolete rows and upserts only changed/new rows. Scoped published name constraints are deferred to allow name swaps; relational checks, publication metadata, and the history entry commit in the same transaction. A database failure returns 503 and rolls everything back. Direct database writes must still be coordinated with maintenance; they are outside the application locking protocol.

The public page endpoint returns site, section, page, ordered sections, and ordered pages from one SQL statement snapshot. This prevents mixed menus/content when a publish happens during page loading. No public refs/notes are returned by this page bundle. There is no publication cache to invalidate in the current clients. An already open page updates when reloaded/navigated; there is no live push.

`workflow.site_publications` stores last publish/unpublish timestamps and a successful publication count. `workflow.publishing_log` records successful publish/unpublish actions and row-change counts. It is an event log, not a content-version archive; prior publication restoration still requires a database backup. Failed attempts do not leave success records. Authentication and access restrictions remain separate deployment work; draft/published separation is not access control.

## API

Crust paths below start at `/api/guten`; Datalake uses `/guten`.

- `GET /publication-status`: status for all draft sites.
- `GET /sites/{site}/publication`: current fingerprints, state, counts and last-published time.
- `POST /publish/{site}` with `{ "expected_fingerprint": "<draft SHA-256>" }`.
- `DELETE /sites/{site}/publication` with `{ "expected_fingerprint": "<published SHA-256>" }`.
- `GET /published/sites/{site}/landing?section={optional}`.
- `GET /published/sites/{site}/page?section={section}&page={page}`: coherent renderer bundle.

Names are scoped by site/section. Unknown or unpublished public addresses return 404. Portal can configure View Published links with `NEXT_PUBLIC_GUTEN_SITES_URL`, defaulting to `http://localhost:3000`.

## Migration and cutover

Migration 002 aligns the empty legacy published tables with draft column names and active fields, adds scoped constraints and publication metadata, and removes independent ID allocation from the five published content tables. It does not modify draft content. Apply the baseline only on a new empty database, then all numbered migrations.

From the sibling `guten` repository, with application writers stopped:

```bash
make backup
make restore ARCHIVE=/absolute/archive TARGET=guten_publish_test_YYYYMMDD
make migrate DATABASE=guten_publish_test_YYYYMMDD
make test TEST_DATABASE=guten_publish_test_YYYYMMDD
make seed-publications DATABASE=guten_publish_test_YYYYMMDD
# After rehearsal, fresh backup and verification:
make migrate DATABASE=guten_datalake ALLOW_MASTER=1
make seed-publications DATABASE=guten_datalake ALLOW_MASTER=1
make backup
make up
```

The seed command is for the initial cutover: it only publishes sites with neither a public copy nor publication history. Re-running it skips already published and deliberately unpublished sites, and can resume after a partial failure. Each site commits separately. It uses an explicit database name and asyncpg's standard PG connection settings. The integration suite only writes to an explicitly selected rehearsal database. It covers draft/public separation, scoped deltas, name swaps, stale requests, simultaneous publication, failure rollback, and unpublish/republish in addition to content editing.
