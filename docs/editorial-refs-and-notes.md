# Editorial references and notes

References and notes belong to a draft page. Portal exposes them below the page editor: create, list, edit/cancel, and confirmed delete. Saving an entry updates its list without reloading the page, preserving unsaved page content and the other editor. Saving the page likewise preserves the attachment forms. They remain absent from Sites and View Draft rendering.

## API

Crust exposes `/api/guten`; Datalake exposes `/guten`.

- `GET /refs` and `GET /notes`: required query parameters `site`, `section`, `page`.
- `POST /refs` and `PUT /refs/{id}`: body includes `site_name`, `section_name`, `page_name`, `url`, and optional `description`.
- `POST /notes` and `PUT /notes/{id}`: body includes the same page scope and `note`.
- `DELETE /refs/{id}` and `DELETE /notes/{id}`: required query parameters `site`, `section`, `page`.

Delete callers must now provide page scope. No unscoped deletion fallback exists. Updates check scope rather than moving the entry to another page. IDs remain unchanged on edit. Unknown pages or entries outside the specified page return 404; missing scope or invalid input returns 422. Valid empty lists return 200. Lists use ascending IDs for stable insertion order; no editorial ordering UI is introduced here.

New/updated URLs must be absolute HTTP/HTTPS URLs no longer than the existing database column limit of 255 characters. Descriptions may be empty. Notes must contain non-whitespace text; Markdown and whitespace are preserved. Existing data is not rewritten. New references receive `external_link` as their internal type; edits preserve an existing type. Type selection and Ref ordering remain future work.

All attachment mutations acquire the same site-row lock as other content writes, then resolve the page and entry within that site. This prevents cross-page mutations and coordinates with deletion. This is relational scope checking, not user authorization; authentication remains future work. Existing foreign keys cascade attachments when their page is deleted. Future reader comments should have a distinct lifecycle from these editorial notes and should not be overwritten by publishing.

## Validation

No database migration is required. `make test TEST_DATABASE=guten_*_test_*` runs the PostgreSQL/FastAPI/Crust integration suite against an explicitly selected rehearsal database. The suite covers CRUD, duplicate page names across parents, invalid/missing scope, URL and note validation, renaming, and deletion cascades alongside ordering tests. Its fixture sites are removed after each test.
