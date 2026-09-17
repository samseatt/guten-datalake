from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from sqlalchemy.exc import IntegrityError
from app.models import Site, Section, Page, Ref, Note
from app.schemas import (SiteCreate, SiteUpdate, SectionCreate, PageCreate, PageResponse,
                         PageCreateResponse)
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
    if (await db.execute(text("SELECT 1 FROM published.sites WHERE id=:id"), {"id": site.id})).scalar():
        raise HTTPException(409, "Unpublish this site before deleting its draft.")
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


async def _attachment_page(db, site, section, page, lock=False):
    # Share the site lock used by page deletion and the future publication flow.
    if lock:
        await _site(db, name=site, lock=True)
    return await get_page_details(db, site, section, page)


async def _attachments(db, model, site, section, page):
    parent = await _attachment_page(db, site, section, page)
    return (await db.execute(select(model).where(model.page_id == parent.id)
                            .order_by(model.id))).scalars().all()


async def _attachment(db, model, item_id, parent_id):
    item = (await db.execute(select(model).where(model.id == item_id,
                                               model.page_id == parent_id))).scalar_one_or_none()
    if item is None:
        raise HTTPException(404, "Reference or note not found in this page")
    return item


async def _write_attachment(db, model, data, item_id=None):
    parent = await _attachment_page(db, data.site_name, data.section_name, data.page_name, lock=True)
    values = data.model_dump(exclude={"site_name", "section_name", "page_name"})
    if item_id is None:
        item = model(page_id=parent.id, **values)
        if model is Ref:
            item.type = "external_link"
        db.add(item)
    else:
        item = await _attachment(db, model, item_id, parent.id)
        for key, value in values.items():
            setattr(item, key, value)
    return await _save(db, item)


async def _delete_attachment(db, model, item_id, site, section, page):
    parent = await _attachment_page(db, site, section, page, lock=True)
    item = await _attachment(db, model, item_id, parent.id)
    await db.delete(item)
    await _save(db)


async def get_refs_by_page(db, site, section, page):
    return await _attachments(db, Ref, site, section, page)


async def create_ref(db, data):
    return await _write_attachment(db, Ref, data)


async def update_ref(db, ref_id, data):
    return await _write_attachment(db, Ref, data, ref_id)


async def delete_ref(db, ref_id, site, section, page):
    await _delete_attachment(db, Ref, ref_id, site, section, page)


async def get_notes_by_page(db, site, section, page):
    return await _attachments(db, Note, site, section, page)


async def create_note(db, data):
    return await _write_attachment(db, Note, data)


async def update_note(db, note_id, data):
    return await _write_attachment(db, Note, data, note_id)


async def delete_note(db, note_id, site, section, page):
    await _delete_attachment(db, Note, note_id, site, section, page)
