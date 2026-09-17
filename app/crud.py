from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from app.models import Site, Section, Page, Ref, Note
from app.schemas import (SiteCreate, SiteUpdate, SectionCreate, PageCreate, PageResponse,
                         RefCreate, RefResponse, NoteCreate, NoteResponse, PageCreateResponse)
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


async def _save(db, obj=None):
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(409, "This change conflicts with an existing name or relationship.") from exc
    if obj is not None:
        await db.refresh(obj)
    return obj


async def _site(db, name=None, site_id=None, lock=False):
    query = select(Site).where(Site.name == name) if name is not None else select(Site).where(Site.id == site_id)
    if lock:
        query = query.with_for_update()
    site = (await db.execute(query)).scalar_one_or_none()
    if site is None:
        raise HTTPException(404, "Site not found")
    return site


async def _section(db, site_id, name):
    section = (await db.execute(select(Section).where(Section.site_id == site_id, Section.name == name))).scalar_one_or_none()
    if section is None:
        raise HTTPException(404, "Section not found in this site")
    return section


async def _validate_landing(db, site_id, page_id):
    if page_id is not None:
        page = (await db.execute(select(Page.id).join(Section, Page.section_id == Section.id)
                                .where(Page.id == page_id, Section.site_id == site_id))).scalar_one_or_none()
        if page is None:
            raise HTTPException(422, "Landing page must belong to this site")


async def get_sites(db: AsyncSession):
    return (await db.execute(select(Site).order_by(Site.id))).scalars().all()


async def get_site_by_name(db: AsyncSession, name: str):
    return await _site(db, name=name)


async def create_site(db: AsyncSession, site: SiteCreate):
    if site.landing_page_id is not None:
        raise HTTPException(422, "Create the site and its pages before selecting a landing page")
    obj = Site(**site.model_dump())
    db.add(obj)
    return await _save(db, obj)


async def update_site(db: AsyncSession, site_name: str, site_data: SiteUpdate):
    site = await _site(db, name=site_name, lock=True)
    await _validate_landing(db, site.id, site_data.landing_page_id)
    for key, value in site_data.model_dump().items():
        setattr(site, key, value)
    return await _save(db, site)


async def delete_site(db: AsyncSession, site_name: str):
    site = await _site(db, name=site_name, lock=True)
    await db.delete(site)
    await _save(db)
    return True


async def get_sections_by_site(db: AsyncSession, site_name: str):
    site = await _site(db, name=site_name)
    return (await db.execute(select(Section).where(Section.site_id == site.id)
                            .order_by(Section.sort_order, Section.id))).scalars().all()


async def get_section_details(db: AsyncSession, site: str, section_name: str):
    parent = await _site(db, name=site)
    return await _section(db, parent.id, section_name)


async def get_section_details_by_id(db: AsyncSession, section_id: int):
    obj = (await db.execute(select(Section).where(Section.id == section_id)
                           .execution_options(populate_existing=True))).scalar_one_or_none()
    if obj is None:
        raise HTTPException(404, "Section not found")
    return obj


async def create_section(db: AsyncSession, section: SectionCreate):
    site = await _site(db, name=section.site_name, lock=True)
    maximum = (await db.execute(select(func.max(Section.sort_order)).where(Section.site_id == site.id))).scalar()
    obj = Section(site_id=site.id, name=section.name, title=section.title, label=section.label,
                  sort_order=0 if maximum is None else maximum + 1)
    db.add(obj)
    return await _save(db, obj)


async def update_section(db: AsyncSession, section_id: int, section):
    obj = await get_section_details_by_id(db, section_id)
    await _site(db, site_id=obj.site_id, lock=True)
    obj = await get_section_details_by_id(db, section_id)
    obj.name, obj.title, obj.label = section.name, section.title, section.label
    return await _save(db, obj)


async def delete_section(db: AsyncSession, section_id: int):
    obj = await get_section_details_by_id(db, section_id)
    await _site(db, site_id=obj.site_id, lock=True)
    obj = await get_section_details_by_id(db, section_id)
    await db.delete(obj)
    await _save(db)


async def get_pages_by_section(db: AsyncSession, site_name: str, section_name: str):
    site = await _site(db, name=site_name)
    section = await _section(db, site.id, section_name)
    return (await db.execute(select(Page).where(Page.section_id == section.id)
                            .order_by(Page.sort_order, Page.id))).scalars().all()


async def get_pages_by_site(db: AsyncSession, site_name: str):
    site = await _site(db, name=site_name)
    rows = (await db.execute(select(Page, Section.name).join(Section, Page.section_id == Section.id)
                            .where(Section.site_id == site.id)
                            .order_by(Section.sort_order, Section.id, Page.sort_order, Page.id))).all()
    return [PageResponse.model_validate(page).model_copy(update={"section_name": section_name})
            for page, section_name in rows]


async def create_page(db: AsyncSession, page_data: PageCreate):
    site = await _site(db, name=page_data.site_name, lock=True)
    section = await _section(db, site.id, page_data.section_name)
    maximum = (await db.execute(select(func.max(Page.sort_order)).where(Page.section_id == section.id))).scalar()
    obj = Page(section_id=section.id, sort_order=0 if maximum is None else maximum + 1,
               **page_data.model_dump(exclude={"site_name", "section_name", "content"}),
               content=page_data.content or "")
    db.add(obj)
    await _save(db, obj)
    return PageCreateResponse(id=obj.id, section_id=obj.section_id, section_name=section.name,
                              sort_order=obj.sort_order, name=obj.name, title=obj.title,
                              primary_image=obj.primary_image, abstract=obj.abstract, content=obj.content)


async def get_page_details(db: AsyncSession, site: str, section: str, page_name: str):
    parent = await _site(db, name=site)
    group = await _section(db, parent.id, section)
    obj = (await db.execute(select(Page).where(Page.section_id == group.id, Page.name == page_name))).scalar_one_or_none()
    if obj is None:
        raise HTTPException(404, "Page not found in this section")
    return obj


async def get_page_details_by_id(db: AsyncSession, page_id: int):
    obj = (await db.execute(select(Page).where(Page.id == page_id)
                           .execution_options(populate_existing=True))).scalar_one_or_none()
    if obj is None:
        raise HTTPException(404, "Page not found")
    return obj


async def _edit_page(db, obj, page):
    # Editing never silently reparents a page or changes its position.
    for key, value in page.model_dump(exclude={"site_name", "section_name"}).items():
        setattr(obj, key, (value or "") if key == "content" else value)
    return await _save(db, obj)


async def update_page(db: AsyncSession, page_name: str, page: PageCreate):
    await _site(db, name=page.site_name, lock=True)
    obj = await get_page_details(db, page.site_name, page.section_name, page_name)
    return await _edit_page(db, obj, page)


async def update_page_by_id(db: AsyncSession, page_id: int, page: PageCreate):
    site = await _site(db, name=page.site_name, lock=True)
    section = await _section(db, site.id, page.section_name)
    obj = await get_page_details_by_id(db, page_id)
    if obj.section_id != section.id:
        raise HTTPException(404, "Page not found in this section")
    return await _edit_page(db, obj, page)


async def delete_page(db: AsyncSession, page_id: int):
    obj = await get_page_details_by_id(db, page_id)
    section = await get_section_details_by_id(db, obj.section_id)
    await _site(db, site_id=section.site_id, lock=True)
    obj = await get_page_details_by_id(db, page_id)
    await db.delete(obj)
    await _save(db)


async def _reorder(db, rows, request):
    current = [row.id for row in rows]
    if current != request.expected_ids:
        raise HTTPException(409, "The list changed. Refresh it before reordering.")
    if set(current) != set(request.ids):
        raise HTTPException(422, "Order must contain every child of this parent exactly once")
    by_id = {row.id: row for row in rows}
    ordered = [by_id[item_id] for item_id in request.ids]
    for position, row in enumerate(ordered):
        row.sort_order = position
    await _save(db)
    return ordered


async def reorder_sections(db, site_name, request):
    await _site(db, name=site_name, lock=True)
    return await _reorder(db, await get_sections_by_site(db, site_name), request)


async def reorder_pages(db, site_name, section_name, request):
    await _site(db, name=site_name, lock=True)
    return await _reorder(db, await get_pages_by_section(db, site_name, section_name), request)


async def get_landing(db, site_name, section_name=None):
    site = await _site(db, name=site_name)
    query = select(Page.name, Section.name).join(Section, Page.section_id == Section.id).where(Section.site_id == site.id)
    if section_name is not None:
        section = await _section(db, site.id, section_name)
        query = query.where(Section.id == section.id)
    elif site.landing_page_id is not None:
        explicit = (await db.execute(query.where(Page.id == site.landing_page_id))).first()
        if explicit:
            return {"page_name": explicit[0], "section_name": explicit[1]}
    row = (await db.execute(query.order_by(Section.sort_order, Section.id, Page.sort_order, Page.id).limit(1))).first()
    if row is None:
        raise HTTPException(404, "No pages in this section" if section_name is not None else "No pages in this site")
    return {"page_name": row[0], "section_name": row[1]}


## Publishing ...

# Publish a site (copy from draft schema to published schema)
async def publish_site(db: AsyncSession, site_name: str):
    logger.info(f"^^^^^^^^^^^^^ publish_site called for site: {site_name}")
    # Copy site
    await db.execute(f"""
        INSERT INTO published.sites (id, name, title)
        SELECT id, name, title FROM draft.sites WHERE name = :site_name
        ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name, title=EXCLUDED.title
    """, {'site_name': site_name})

    logger.info(f"^^^^^^^^^^^^^ Site copied for: {site_name}")

    # Copy sections
    await db.execute(f"""
        INSERT INTO published.sections (id, site_id, name, title)
        SELECT sections.id, sections.site_id, sections.name, sections.title
        FROM draft.sections
        JOIN draft.sites ON draft.sections.site_id = draft.sites.id
        WHERE draft.sites.name = :site_name
        ON CONFLICT (id) DO UPDATE SET 
            site_id=EXCLUDED.site_id, name=EXCLUDED.name, title=EXCLUDED.title
    """, {'site_name': site_name})

    logger.info(f"^^^^^^^^^^^^^ Sections copied for: {site_name}")

    # Copy pages
    await db.execute(f"""
        INSERT INTO published.pages (id, section_id, name, title, abstract, content)
        SELECT pages.id, pages.section_id, pages.name, pages.title, pages.abstract, pages.content
        FROM draft.pages
        JOIN draft.sections ON pages.section_id = sections.id
        JOIN draft.sites ON sections.site_id = sites.id
        WHERE sites.name = :site_name
        ON CONFLICT (id) DO UPDATE SET 
            section_id=EXCLUDED.section_id, name=EXCLUDED.name, title=EXCLUDED.title,
            abstract=EXCLUDED.abstract, content=EXCLUDED.content
    """, {'site_name': site_name})

    logger.info(f"^^^^^^^^^^^^^ Pages copied for: {site_name}")

    await db.commit()
    logger.info(f"^^^^^^^^^^^^^ Published completed and committed for: {site_name}")

# Get published page
async def get_published_page(db: AsyncSession, site_name: str, page_name: str):
    result = await db.execute(
        select(Page).join(Section).join(Site)
        .options(selectinload(Page.section))
        .where(
            Site.name == site_name,
            Page.name == page_name
        ).execution_options(schema_translate_map={'schema': 'published'})
    )
    return result.scalar_one_or_none()


async def get_refs_by_page(db: AsyncSession, site: str, section: str, page: str):
    result = await db.execute(
        select(Ref).join(Page).join(Section).join(Site)
        .where(Site.name == site, Section.name == section, Page.name == page)
    )
    return result.scalars().all()

# Create a new ref
async def create_ref(db: AsyncSession, ref_data: RefCreate):
    site = await db.execute(select(Site).where(Site.name == ref_data.site_name))
    site_instance = site.scalar_one_or_none()
    if not site_instance:
        raise HTTPException(status_code=404, detail="Site not found")

    section = await db.execute(select(Section).where(Section.site_id == site_instance.id, Section.name == ref_data.section_name))
    section_instance = section.scalar_one_or_none()
    if not section_instance:
        raise HTTPException(status_code=404, detail="Section not found")

    page = await db.execute(select(Page).where(Page.section_id == section_instance.id, Page.name == ref_data.page_name))
    page_instance = page.scalar_one_or_none()
    if not page_instance:
        raise HTTPException(status_code=404, detail="Page not found")

    new_ref = Ref(
        page_id=page_instance.id,
        description=ref_data.description,
        url=ref_data.url,
    )
    logger.info(f"############ Creating a new ref: {new_ref.description}")
    db.add(new_ref)
    logger.info(f"############ New ref added: {new_ref.description}")
    await db.commit()
    logger.info(f"############ New ref committed: {new_ref.description}")
    await db.refresh(new_ref)
    logger.info(f"############ New ref refreshed: {new_ref.description}")

    return RefResponse(
        id=new_ref.id,
        page_id=new_ref.page_id,
        url=new_ref.url,
        type=new_ref.type,
        description=new_ref.description
    )

# Update a ref
async def update_ref(db: AsyncSession, ref_id: int, ref: RefCreate):
    logger.info(f"crud. update_ref called with ref id: {ref_id}")
    query = await db.execute(select(Ref).where(Ref.id == ref_id))
    ref_instance = query.scalar_one_or_none()

    if not ref_instance:
        raise HTTPException(status_code=404, detail="Ref not found")

    ref_instance.description = ref.description
    ref_instance.url = ref.url

    await db.commit()
    await db.refresh(ref_instance)
    return ref_instance


# Delete a ref
async def delete_ref(db: AsyncSession, ref_id: int):
    query = await db.execute(select(Ref).where(Ref.id == ref_id))
    ref_instance = query.scalar_one_or_none()

    if not ref_instance:
        raise HTTPException(status_code=404, detail="Ref not found")

    await db.delete(ref_instance)
    await db.commit()


async def get_notes_by_page(db: AsyncSession, site: str, section: str, page: str):
    result = await db.execute(
        select(Note).join(Page).join(Section).join(Site)
        .where(Site.name == site, Section.name == section, Page.name == page)
    )
    return result.scalars().all()

# Create a new note
async def create_note(db: AsyncSession, note_data: NoteCreate):
    site = await db.execute(select(Site).where(Site.name == note_data.site_name))
    site_instance = site.scalar_one_or_none()
    if not site_instance:
        raise HTTPException(status_code=404, detail="Site not found")

    section = await db.execute(select(Section).where(Section.site_id == site_instance.id, Section.name == note_data.section_name))
    section_instance = section.scalar_one_or_none()
    if not section_instance:
        raise HTTPException(status_code=404, detail="Section not found")

    page = await db.execute(select(Page).where(Page.section_id == section_instance.id, Page.name == note_data.page_name))
    page_instance = page.scalar_one_or_none()
    if not page_instance:
        raise HTTPException(status_code=404, detail="Page not found")

    new_note = Note(
        page_id=page_instance.id,
        note=note_data.note,
    )
    logger.info(f"############ Creating a new note: {new_note.id}")
    db.add(new_note)
    logger.info(f"############ New note added: {new_note.id}")
    await db.commit()
    logger.info(f"############ New note committed: {new_note.id}")
    await db.refresh(new_note)
    logger.info(f"############ New note refreshed: {new_note.id}")

    return NoteResponse(
        id=new_note.id,
        page_id=new_note.page_id,
        note=new_note.note,
    )

# Delete a note
async def delete_note(db: AsyncSession, note_id: int):
    query = await db.execute(select(Note).where(Note.id == note_id))
    note_instance = query.scalar_one_or_none()

    if not note_instance:
        raise HTTPException(status_code=404, detail="Note not found")

    await db.delete(note_instance)
    await db.commit()

