"""Atomic per-site publication and coherent published reads.

Identifiers below are application constants, never request-supplied SQL identifiers.
A single JSON snapshot captures all supported content. Every write uses that captured
snapshot, so direct SQL edits during a publish cannot produce a mixed copy.
"""
import hashlib
import json
from fastapi import HTTPException
from sqlalchemy import text
from app.crud import _site

TABLES = ("sites", "sections", "pages", "refs", "notes")
COLUMNS = {
    "sites": "id,name,title,logo,url,created_at,updated_at,landing_page_id,favicon,color",
    "sections": "id,site_id,name,section_theme_id,sort_order,created_at,updated_at,title,label",
    "pages": "id,section_id,template_id,name,primary_image,abstract,content,tags,sort_order,created_at,updated_at,title",
    "refs": "id,page_id,url,description,type,sort_order",
    "notes": "id,page_id,note,created_at",
}


def predicate(schema, table):
    sections = f"SELECT id FROM {schema}.sections WHERE site_id = :site_id"
    pages = f"SELECT id FROM {schema}.pages WHERE section_id IN ({sections})"
    return {"sites": "id = :site_id", "sections": "site_id = :site_id",
            "pages": f"section_id IN ({sections})", "refs": f"page_id IN ({pages})",
            "notes": f"page_id IN ({pages})"}[table]


def snapshot_sql(schema):
    assert schema in ("draft", "published")
    parts = []
    for table in TABLES:
        parts.append(f"'{table}', COALESCE((SELECT jsonb_agg(to_jsonb(t) ORDER BY t.id) "
                     f"FROM {schema}.{table} t WHERE {predicate(schema, table)}), '[]'::jsonb)")
    return "jsonb_build_object(" + ",".join(parts) + ")"


def fingerprint(snapshot):
    return hashlib.sha256(json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


async def snapshots(db, site_id):
    row = (await db.execute(text(f"SELECT {snapshot_sql('draft')} AS draft, "
                                f"{snapshot_sql('published')} AS published"), {"site_id": site_id})).mappings().one()
    return row["draft"], row["published"]


async def status_for(db, site_id):
    draft, published = await snapshots(db, site_id)
    history = (await db.execute(text("SELECT last_published_at, last_unpublished_at, publish_count "
                                    "FROM workflow.site_publications WHERE site_id = :site_id"),
                               {"site_id": site_id})).mappings().first()
    live = bool(published["sites"])
    return {"site_id": site_id, "is_published": live,
            "section_count": len(draft["sections"]), "page_count": len(draft["pages"]),
            "has_changes": not live or fingerprint(draft) != fingerprint(published),
            "draft_fingerprint": fingerprint(draft),
            "published_fingerprint": fingerprint(published) if live else None,
            "last_published_at": history["last_published_at"] if history else None,
            "last_unpublished_at": history["last_unpublished_at"] if history else None,
            "publish_count": history["publish_count"] if history else 0}


async def get_status(db, site_name):
    site = await _site(db, name=site_name)
    return await status_for(db, site.id)


async def all_statuses(db):
    ids = (await db.execute(text("SELECT id FROM draft.sites ORDER BY id"))).scalars().all()
    return [await status_for(db, site_id) for site_id in ids]


async def _log(db, site_id, action, details):
    await db.execute(text("INSERT INTO workflow.publishing_log(site_id, action, details) "
                          "VALUES (:site_id, :action, :details)"),
                     {"site_id": site_id, "action": action, "details": json.dumps(details, sort_keys=True)})


async def publish_site(db, site_name, expected_fingerprint):
    await db.execute(text("SET LOCAL lock_timeout = '5s'"))
    await db.execute(text("SET LOCAL statement_timeout = '30s'"))
    site = await _site(db, name=site_name, lock=True)
    draft, published = await snapshots(db, site.id)
    if fingerprint(draft) != expected_fingerprint:
        raise HTTPException(409, "Draft changed. Refresh publication status and review it before publishing.")
    if any(p["template_id"] is not None for p in draft["pages"]) or any(s["section_theme_id"] is not None for s in draft["sections"]):
        raise HTTPException(422, "Template/theme assignments are not supported by this publishing workflow yet.")
    landing = draft["sites"][0]["landing_page_id"]
    if landing is not None and landing not in {p["id"] for p in draft["pages"]}:
        raise HTTPException(422, "Landing page must belong to this site")
    if draft == published:
        result = await status_for(db, site.id)
        await db.commit()
        return {**result, "changed": False}

    changes = {}
    # Delete stale children first. Existing cascading FKs remain in force.
    for table in reversed(TABLES[1:]):
        keep = [row["id"] for row in draft[table]]
        result = await db.execute(text(f"DELETE FROM published.{table} WHERE {predicate('published', table)} "
                                       "AND NOT (id = ANY(CAST(:ids AS integer[])))"),
                                  {"site_id": site.id, "ids": keep})
        changes[table] = {"deleted": result.rowcount}
    # Deferrable scoped-name constraints allow renames/name swaps in one publication.
    for table in TABLES:
        columns = COLUMNS[table]
        fields = [c for c in columns.split(",") if c != "id"]
        assignments = ",".join(f"{c}=EXCLUDED.{c}" for c in fields)
        old = ",".join(f"target.{c}" for c in fields)
        new = ",".join(f"EXCLUDED.{c}" for c in fields)
        sql = f"""INSERT INTO published.{table} AS target ({columns})
            SELECT {columns} FROM jsonb_populate_recordset(NULL::published.{table}, CAST(:rows AS jsonb))
            ON CONFLICT (id) DO UPDATE SET {assignments}
            WHERE ROW({old}) IS DISTINCT FROM ROW({new})"""
        result = await db.execute(text(sql), {"rows": json.dumps(draft[table])})
        changes.setdefault(table, {})["inserted_or_updated"] = result.rowcount
    await db.execute(text("""INSERT INTO workflow.site_publications(site_id,last_published_at)
        VALUES (:site_id,clock_timestamp()) ON CONFLICT (site_id) DO UPDATE
        SET last_published_at=clock_timestamp(), last_unpublished_at=NULL,
            publish_count=workflow.site_publications.publish_count+1"""), {"site_id": site.id})
    await _log(db, site.id, "publish", {"fingerprint": fingerprint(draft), "changes": changes})
    # Force deferred checks before responding. Any failure rolls back the complete copy.
    await db.execute(text("SET CONSTRAINTS ALL IMMEDIATE"))
    result = await status_for(db, site.id)
    await db.commit()
    return {**result, "changed": True}


async def unpublish_site(db, site_name, expected_fingerprint):
    site = await _site(db, name=site_name, lock=True)
    _, published = await snapshots(db, site.id)
    if not published["sites"]:
        raise HTTPException(409, "This site is already unpublished. Refresh publication status.")
    if fingerprint(published) != expected_fingerprint:
        raise HTTPException(409, "Published content changed. Refresh publication status before unpublishing.")
    await db.execute(text("DELETE FROM published.sites WHERE id=:site_id"), {"site_id": site.id})
    await db.execute(text("UPDATE workflow.site_publications SET last_unpublished_at=clock_timestamp() "
                          "WHERE site_id=:site_id"), {"site_id": site.id})
    await _log(db, site.id, "unpublish", {"fingerprint": fingerprint(published)})
    result = await status_for(db, site.id)
    await db.commit()
    return result


async def published_snapshot(db, name):
    # The name lookup and all five tables use the same statement snapshot.
    sql = (f"SELECT {snapshot_sql('published')} FROM "
           "(SELECT id AS site_id FROM published.sites WHERE name=:name) selected")
    sql = sql.replace(":site_id", "selected.site_id")
    result = (await db.execute(text(sql), {"name": name})).scalar_one_or_none()
    if result is None:
        raise HTTPException(404, "Published site not found")
    return result


def ordered(rows):
    return sorted(rows, key=lambda row: (row["sort_order"], row["id"]))


async def published_landing(db, site_name, section_name=None):
    data = await published_snapshot(db, site_name)
    sections = ordered(data["sections"])
    if section_name is not None:
        sections = [s for s in sections if s["name"] == section_name]
        if not sections:
            raise HTTPException(404, "Published section not found")
    pages = [p for s in sections for p in ordered(data["pages"]) if p["section_id"] == s["id"]]
    if not pages:
        raise HTTPException(404, "No published page is available at this address")
    landing = data["sites"][0]["landing_page_id"] if section_name is None else None
    page = next((p for p in pages if p["id"] == landing), pages[0])
    section = next(s for s in sections if s["id"] == page["section_id"])
    return {"section_name": section["name"], "page_name": page["name"]}


async def published_page(db, site_name, section_name, page_name):
    data = await published_snapshot(db, site_name)
    section = next((s for s in data["sections"] if s["name"] == section_name), None)
    if section is None:
        raise HTTPException(404, "Published section not found")
    pages = ordered([p for p in data["pages"] if p["section_id"] == section["id"]])
    page = next((p for p in pages if p["name"] == page_name), None)
    if page is None:
        raise HTTPException(404, "Published page not found")
    return {"site": data["sites"][0], "section": section, "page": page,
            "sections": ordered(data["sections"]), "pages": pages}
