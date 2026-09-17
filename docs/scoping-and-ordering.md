# Scoped names and ordering

## Schema and migration

`draft.sites.name` remains globally unique. Sections are unique by `(site_id, name)`, pages by `(section_id, name)`. Their parent references and titles are non-null. Sections and pages have non-null, nonnegative `sort_order`; reads use `(sort_order, id)` within their parent. The migration initializes consecutive zero-based positions, preserving existing sort values first and using IDs to break ties. It does not change existing IDs, names, content, image paths, or landing selections.

`scripts/database/schema.sql` is the audited **pre-migration baseline** captured on 2026-09-17. For a new empty Guten database, import that baseline, then run the numbered migrations. For an existing database or archive restore, run migrations only. Never rerun the baseline on the master. `workflow.schema_migrations` records SHA-256 checksums, and the runner refuses changed or unknown applied migrations. All pending migrations apply in one transaction under an advisory lock. No automatic down-migration is supplied: restoring global page-name uniqueness after accepting duplicate names would not be safe.

From the sibling guten coordination repository:

```bash
make backup
make restore ARCHIVE=/absolute/path/to/archive TARGET=guten_ordering_test_YYYYMMDD
make migrate DATABASE=guten_ordering_test_YYYYMMDD
make test TEST_DATABASE=guten_ordering_test_YYYYMMDD
# After successful rehearsal and a fresh backup, with application writers stopped:
make migrate DATABASE=guten_datalake ALLOW_MASTER=1
```

The runner uses standard PostgreSQL PG* environment variables. It does not consume SQLAlchemy DATABASE_URL. Tests start isolated FastAPI/Crust processes, target only explicitly named guten_*_test_* databases, and remove their own fixture sites. Test fixture inserts advance sequences in the rehearsal database; tests never run against the master.

## API contract

Datalake endpoints use `/guten`; Crust exposes the same paths under `/api/guten`.

- `PUT /sites/{site_name}/sections/order`
- `PUT /sites/{site_name}/sections/{section_name}/pages/order`

Both accept `{ "ids": [3, 1, 2], "expected_ids": [1, 2, 3] }`. IDs must be positive integers with no duplicates. `ids` must contain exactly the current parent's children. `expected_ids` must match the current ordered list. Invalid membership returns 422; stale membership/order returns 409. Writes lock the site row, serializing application section/page create, update, delete, and reorder operations for that site. All positions update in one transaction. Direct SQL writers must use the same discipline or run during maintenance.

New children append after the current maximum position. Deletion may leave gaps; the next reorder normalizes them. Renames/content edits retain IDs, parent, and order. Editing by ID refuses a mismatched requested site/section rather than silently moving the page. Existing ID-based mutation routes remain for compatibility; ownership/auth is not implemented by this change.

Section/page read responses include `sort_order`. `/pages_all/{site_name}` is ordered by section then page and includes `section_name` for landing-dropdown disambiguation. Names remain URL-facing identifiers; IDs remain relational identifiers and stable reorder payload values.

`GET /sites/{site_name}/landing?section={optional_section}` returns `{ "section_name": "...", "page_name": "..." }`. Site-level lookup prefers a valid explicit landing page, otherwise the first page of the first nonempty section. Section-level lookup returns that section's first page. Missing/empty resources return 404. Site updates validate same-site landing selection, and the existing FK clears a landing selection if its page is deleted.

## UI and publication boundary

Portal section/page lists have accessible Move Up/Down buttons, disabled during requests, and inline save/conflict feedback. On a failed mutation they refresh the list. View Draft consumes ordered draft APIs. Following migration 002, Guten Sites consumes ordered published snapshots with the same landing-selection rules. They retain independent layouts and URL prefixes. See [publishing](publishing.md).

Migration 001 addressed draft scoping and ordering only. Migration 002 and the current publication service add the published boundary; editorial refs/notes CRUD is also now supported. Authentication and centralized media storage remain future work.
