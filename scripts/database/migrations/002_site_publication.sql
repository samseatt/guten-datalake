-- Align the legacy published schema without touching draft content.
ALTER TABLE published.sites RENAME COLUMN site_name TO name;
ALTER TABLE published.sites RENAME COLUMN site_title TO title;
ALTER TABLE published.sites RENAME COLUMN site_logo TO logo;
ALTER TABLE published.sites RENAME COLUMN site_url TO url;
ALTER TABLE published.sites ADD COLUMN landing_page_id integer,
    ADD COLUMN favicon text, ADD COLUMN color text;
ALTER TABLE published.sections RENAME COLUMN section_name TO name;
ALTER TABLE published.sections ADD COLUMN title text, ADD COLUMN label text;
UPDATE published.sections SET title = name WHERE title IS NULL;
ALTER TABLE published.sections ALTER COLUMN title SET NOT NULL,
    ALTER COLUMN sort_order SET NOT NULL,
    ADD CONSTRAINT sections_site_name_key UNIQUE (site_id, name) DEFERRABLE INITIALLY DEFERRED,
    ADD CONSTRAINT sections_sort_order_check CHECK (sort_order >= 0);
ALTER TABLE published.pages RENAME COLUMN page_name TO name;
ALTER TABLE published.pages ADD COLUMN title text;
UPDATE published.pages SET title = name WHERE title IS NULL;
ALTER TABLE published.pages ALTER COLUMN title SET NOT NULL,
    ALTER COLUMN sort_order SET NOT NULL,
    DROP CONSTRAINT pages_page_name_key,
    ADD CONSTRAINT pages_section_name_key UNIQUE (section_id, name) DEFERRABLE INITIALLY DEFERRED,
    ADD CONSTRAINT pages_sort_order_check CHECK (sort_order >= 0);
ALTER TABLE published.sites ADD CONSTRAINT sites_landing_page_fkey
    FOREIGN KEY (landing_page_id) REFERENCES published.pages(id) ON DELETE SET NULL
    DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX sections_site_order_idx ON published.sections(site_id, sort_order, id);
CREATE INDEX pages_section_order_idx ON published.pages(section_id, sort_order, id);
CREATE INDEX refs_page_idx ON published.refs(page_id);
CREATE INDEX notes_page_idx ON published.notes(page_id);
-- Published identities always come from draft. Do not allocate unrelated IDs here.
ALTER TABLE published.sites ALTER COLUMN id DROP DEFAULT;
ALTER TABLE published.sections ALTER COLUMN id DROP DEFAULT;
ALTER TABLE published.pages ALTER COLUMN id DROP DEFAULT;
ALTER TABLE published.refs ALTER COLUMN id DROP DEFAULT;
ALTER TABLE published.notes ALTER COLUMN id DROP DEFAULT;

CREATE TABLE workflow.site_publications (
    site_id integer PRIMARY KEY REFERENCES draft.sites(id) ON DELETE CASCADE,
    last_published_at timestamptz NOT NULL,
    last_unpublished_at timestamptz,
    publish_count integer NOT NULL DEFAULT 1 CHECK (publish_count > 0)
);
ALTER TABLE workflow.publishing_log DROP CONSTRAINT publishing_log_action_check;
ALTER TABLE workflow.publishing_log ADD CONSTRAINT publishing_log_action_check
    CHECK (action IN ('publish', 'rollback', 'update', 'unpublish'));
