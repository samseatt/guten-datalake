from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud import (
    get_sections_by_site, get_section_details, get_section_details_by_id,
    create_section, update_section, delete_section
)
from app.schemas import SectionCreate, SectionUpdate, SectionResponse
import logging

# Logger for this file
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/sections", response_model=list[SectionResponse])
async def get_sections(site: str, db: AsyncSession = Depends(get_db)):
    return await get_sections_by_site(db, site)

@router.get("/sections/{section_name}", response_model=SectionResponse)
async def section_detail(section_name: str, site: str, db: AsyncSession = Depends(get_db)):
    section = await get_section_details(db, site, section_name)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section

# Get a section by its ID only
@router.get("/section_by_id/{section_id}", response_model=SectionResponse)
async def section_detail_by_id(section_id: int, db: AsyncSession = Depends(get_db)):
    section = await get_section_details_by_id(db, section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section

# Create a new section 
@router.post("/sections", response_model=SectionResponse)
async def create_new_section(section: SectionCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"$$$$$$$$$$$ create_new_section called")
    return await create_section(db, section)

# Update a section
@router.put("/sections/{section_id}", response_model=SectionResponse)
async def update_existing_section(section_id: int, section: SectionUpdate, db: AsyncSession = Depends(get_db)):
    logger.info(f"update_existing_section called with section id: {section_id}")
    return await update_section(db, section_id, section)

# @router.put("/sites/{site_name}")
# async def update_site(site_name: str, site: SiteUpdate, db: AsyncSession = Depends(get_db)):
#     logger.info(f"$$$$$$$$$$$ update_site called with site_name: {site_name}")
#     updated_site = await crud.update_site(db, site_name, site)
#     logger.info(f"$$$$$$$$$$$ update_site returned {update_site}")
#     if not updated_site:
#         raise HTTPException(status_code=404, detail="Site not found")
#     return updated_site

@router.delete("/sections/{section_id}")
async def remove_section(section_id: int, db: AsyncSession = Depends(get_db)):
    logger.info(f"remove_section called with section id: {section_id}")
    await delete_section(db, section_id)
    return {"message": "Section deleted successfully"}
