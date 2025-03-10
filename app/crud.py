from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import update, delete
from app.models import Site, Section, Page, Ref, Note
from app.schemas import SiteCreate, SiteUpdate, SectionCreate, PageCreate, PageResponse, RefCreate, RefResponse, NoteCreate, NoteResponse, PageCreateResponse
from fastapi import HTTPException
import logging

# Logger for this file
logger = logging.getLogger(__name__)

## Sites ...

# Get all sites in the system
async def get_sites(db: AsyncSession):
    result = await db.execute(select(Site))
    return result.scalars().all()

# Get a site by its unique name
async def get_site_by_name(db: AsyncSession, name: str):
    result = await db.execute(select(Site).filter(Site.name == name))
    return result.scalar_one_or_none()

# Create a new site
async def create_site(db: AsyncSession, site: SiteCreate):
    new_site = Site(**site.dict())
    db.add(new_site)
    await db.commit()
    await db.refresh(new_site)
    return new_site

# Update site
async def update_site(db: AsyncSession, site_name: str, site_data: SiteUpdate):
    logger.info(f"$$$$$$$$$$$ crud.update_site called with site_name: {site_name}")
    result = await db.execute(select(Site).filter(Site.name == site_name))
    logger.info(f"$$$$$$$$$$$ crud.update_site returned: {result}")
    site = result.scalar_one_or_none()
    logger.info(f"$$$$$$$$$$$ crud.update_site returned: {site.title}")
    if not site:
        return None

    site.title = site_data.title
    site.url = site_data.url
    site.logo = site_data.logo
    site.favicon = site_data.favicon
    site.color = site_data.color
    site.landing_page_id = site_data.landing_page_id
    await db.commit()
    await db.refresh(site)
    logger.info(f"$$$$$$$$$$$ crud.update_site returning: {site.title}")
    return site

# Delete site
async def delete_site(db: AsyncSession, site_name: str):
    result = await db.execute(select(Site).filter(Site.name == site_name))
    site = result.scalar_one_or_none()
    if not site:
        return False

    await db.delete(site)
    await db.commit()
    return True

## Sections ...

# Get all sections for a given site
async def get_sections_by_site(db: AsyncSession, site_name: str):
    result = await db.execute(
        select(Section).join(Site).where(Site.name == site_name)
    )
    return result.scalars().all()

# Get a single section givin its unique name within a site
async def get_section_details(db: AsyncSession, site: str, section_name: str):
    result = await db.execute(
        select(Section).join(Site)
        .where(Site.name == site, Section.name == section_name)
    )
    return result.scalar_one_or_none()

# Get a single section givin its unique id
async def get_section_details_by_id(db: AsyncSession, section_id: int):
    result = await db.execute(
        select(Section)
        .where(Section.id == section_id)
    )
    return result.scalar_one_or_none()

# Create a new section
async def create_section(db: AsyncSession, section: SectionCreate):
    logger.info(f"%%%%%%%%%% Calling create_section")
    site = await db.execute(select(Site).where(Site.name == section.site_name))
    site_instance = site.scalar_one_or_none()
    if not site_instance:
        raise HTTPException(status_code=404, detail="Site not found")

    logger.info(f"%%%%%%%%%% Found site: {section.site_name}")

    new_section = Section(
        site_id=site_instance.id,
        name=section.name,
        title=section.title,
        label=section.label
    )
    
    logger.info(f"%%%%%%%%%% Created a new section for site: {site_instance.id}")

    db.add(new_section)
    await db.commit()
    await db.refresh(new_section)
    return new_section

# Update a section
async def update_section(db: AsyncSession, section_id: int, section: SectionCreate):
    logger.info(f"crud. update_section called with section id: {section_id}")
    query = await db.execute(select(Section).where(Section.id == section_id))
    section_instance = query.scalar_one_or_none()

    if not section_instance:
        raise HTTPException(status_code=404, detail="Section not found")

    section_instance.name = section.name
    section_instance.title = section.title
    section_instance.label = section.label

    await db.commit()
    await db.refresh(section_instance)
    return section_instance

# Delete a section
async def delete_section(db: AsyncSession, section_id: int):
    query = await db.execute(select(Section).where(Section.id == section_id))
    section_instance = query.scalar_one_or_none()

    if not section_instance:
        raise HTTPException(status_code=404, detail="Section not found")

    await db.delete(section_instance)
    await db.commit()

## Pages ...

# async def get_pages_by_section(db: AsyncSession, section_name: str):
#     result = await db.execute(
#         select(Page).join(Section).filter(Section.name == section_name)
#     )
#     return result.scalars().all()
async def get_pages_by_section(db: AsyncSession, site: str, section: str):
    result = await db.execute(
        select(Page).join(Section).join(Site)
        .where(Site.name == site, Section.name == section)
    )
    return result.scalars().all()

# Fetch Pages by Section
async def get_pages_by_section(db: AsyncSession, site_name: str, section_name: str):
    logger.info(f"$$$$$$$$$ crud.get_pages_by_section called with {site_name}, {section_name}")
    result = await db.execute(
        select(Page)
        .join(Section)
        .join(Site)
        .filter(Site.name == site_name)
        .filter(Section.name == section_name)
    )
    pages_found = result.scalars().all()
    return pages_found
    # return result.scalars().all()

# Fetch Pages by Site
async def get_pages_by_site(db: AsyncSession, site_name: str):
    logger.info(f"$$$$$$$$$ crud.get_pages_by_site called with {site_name}")
    result = await db.execute(
        select(Page)
        .join(Section)
        .join(Site)
        .filter(Site.name == site_name)
    )
    pages_found = result.scalars().all()
    return pages_found
    # return result.scalars().all()

# Create a new page
async def create_page(db: AsyncSession, page_data: PageCreate):
    site = await db.execute(select(Site).where(Site.name == page_data.site_name))
    site_instance = site.scalar_one_or_none()
    if not site_instance:
        raise HTTPException(status_code=404, detail="Site not found")

    section = await db.execute(select(Section).where(Section.name == page_data.section_name))
    section_instance = section.scalar_one_or_none()
    if not section_instance:
        raise HTTPException(status_code=404, detail="Section not found")

    new_page = Page(
        section_id=section_instance.id,
        name=page_data.name,
        title=page_data.title,
        primary_image=page_data.primary_image,
        abstract=page_data.abstract,
        content=page_data.content
    )
    logger.info(f"############ Creating a new page: {new_page.name}")
    db.add(new_page)
    logger.info(f"############ New page added: {new_page.name}")
    await db.commit()
    logger.info(f"############ New page committed: {new_page.name}")
    await db.refresh(new_page)
    logger.info(f"############ New page refreshed: {new_page.name}")

    return PageCreateResponse(
        id=new_page.id,
        site_name=site_instance.name,
        section_name=section_instance.name,
        name=new_page.name,
        title=new_page.title,
        primary_image=new_page.primary_image,
        abstract=new_page.abstract,
        content=new_page.content
    )

# Single page retrieval
async def get_page_details(db: AsyncSession, site: str, section: str, page_name: str):
    result = await db.execute(
        select(Page).join(Section).join(Site)
        .where(
            Site.name == site,
            Section.name == section,
            Page.name == page_name
        )
    )
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page

# Single page retrieval by ID
async def get_page_details_by_id(db: AsyncSession, page_id: int):
    result = await db.execute(
        select(Page).join(Section)
        .where(
            Section.id == Page.section_id,
            Page.id == page_id
        )
    )
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page

# Update a page
async def update_page(db: AsyncSession, page_name: str, page: PageCreate):
    query = await db.execute(select(Page).join(Section).join(Site)
        .where(Page.name == page_name,
               Section.name == page.section_name,
               Site.name == page.site_name
        )
    )
    page_instance = query.scalar_one_or_none()

    if not page_instance:
        raise HTTPException(status_code=404, detail="Page not found")

    section_query = await db.execute(select(Section).join(Site)
                                     .where(Section.name == page.section_name, 
                                            Site.name == page.site_name))
    section_instance = section_query.scalar_one_or_none()
    if not section_instance:
        raise HTTPException(status_code=404, detail="Section not found")

    page_instance.section_id = section_instance.id
    page_instance.name = page.name
    page_instance.title = page.title
    page_instance.primary_image = page.primary_image
    page_instance.abstract = page.abstract
    page_instance.content = page.content

    await db.commit()
    await db.refresh(page_instance)
    return page_instance

# Update a page
async def update_page_by_id(db: AsyncSession, page_id: int, page: PageCreate):
    query = await db.execute(select(Page).where(Page.id == page_id))
    page_instance = query.scalar_one_or_none()

    if not page_instance:
        raise HTTPException(status_code=404, detail="Page not found")

    section_query = await db.execute(select(Section).join(Site)
                                     .where(Section.name == page.section_name, 
                                            Site.name == page.site_name))
    section_instance = section_query.scalar_one_or_none()
    if not section_instance:
        raise HTTPException(status_code=404, detail="Section not found")

    page_instance.section_id = section_instance.id
    page_instance.name = page.name
    page_instance.title = page.title
    page_instance.abstract = page.abstract
    page_instance.content = page.content

    await db.commit()
    await db.refresh(page_instance)
    return page_instance

# Delete a page
async def delete_page(db: AsyncSession, page_id: int):
    query = await db.execute(select(Page).where(Page.id == page_id))
    page_instance = query.scalar_one_or_none()

    if not page_instance:
        raise HTTPException(status_code=404, detail="Page not found")

    await db.delete(page_instance)
    await db.commit()

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

