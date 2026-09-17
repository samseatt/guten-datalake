-- Preserve content and identity; normalize positions independently per parent.
WITH ordered AS (
    SELECT id, row_number() OVER (PARTITION BY site_id ORDER BY sort_order NULLS LAST, id) - 1 AS position
    FROM draft.sections
)
UPDATE draft.sections s SET sort_order = ordered.position FROM ordered WHERE s.id = ordered.id;
WITH ordered AS (
    SELECT id, row_number() OVER (PARTITION BY section_id ORDER BY sort_order NULLS LAST, id) - 1 AS position
    FROM draft.pages
)
UPDATE draft.pages p SET sort_order = ordered.position FROM ordered WHERE p.id = ordered.id;

ALTER TABLE draft.sections
    ALTER COLUMN site_id SET NOT NULL,
    ALTER COLUMN title SET NOT NULL,
    ALTER COLUMN sort_order SET DEFAULT 0,
    ALTER COLUMN sort_order SET NOT NULL,
    ADD CONSTRAINT sections_site_name_key UNIQUE (site_id, name),
    ADD CONSTRAINT sections_sort_order_check CHECK (sort_order >= 0);
ALTER TABLE draft.pages
    ALTER COLUMN section_id SET NOT NULL,
    ALTER COLUMN title SET NOT NULL,
    ALTER COLUMN sort_order SET DEFAULT 0,
    ALTER COLUMN sort_order SET NOT NULL,
    DROP CONSTRAINT pages_page_name_key,
    ADD CONSTRAINT pages_section_name_key UNIQUE (section_id, name),
    ADD CONSTRAINT pages_sort_order_check CHECK (sort_order >= 0);
CREATE INDEX sections_site_order_idx ON draft.sections (site_id, sort_order, id);
CREATE INDEX pages_section_order_idx ON draft.pages (section_id, sort_order, id);
