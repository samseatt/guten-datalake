from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud import (
    get_pages_by_section, get_page_details, get_page_details_by_id, get_pages_by_site, create_page,
    update_page, delete_page
)
from app.schemas import PageCreate, PageResponse, PageCreateResponse
import logging

# Logger for this file
logger = logging.getLogger(__name__)

router = APIRouter()

# @router.get("/pages")
# async def read_pages(section: str, db: AsyncSession = Depends(get_db)):
#     return await get_pages_by_section(db, section)

# @router.post("/pages", response_model=PageResponse)
# async def create_new_page(page: PageCreate, db: AsyncSession = Depends(get_db)):
#     try:
#         new_page = await create_page(db, page)
#         return new_page
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@router.get("/pages", response_model=list[PageResponse])
# async def read_pages(section: str, db: AsyncSession = Depends(get_db)):
#     return await get_pages_by_section(db, section)
async def read_pages(site: str, section: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"@@@@@@@@@@@@@@ read_pages called with site: {site}, section: {section}")
    return await get_pages_by_section(db, site, section)

# @router.get("/pages/{page_name}", response_model=PageResponse)
# async def read_page(page_name: str, section: str, db: AsyncSession = Depends(get_db)):
#     page = await get_page_details(db, section, page_name)
#     if not page:
#         raise HTTPException(status_code=404, detail="Page not found")
#     return page
@router.get("/pages/{page_name}", response_model=PageResponse)
async def read_page(page_name: str, site: str, section: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"&&&&&&&&&&& read_page called with site: {site}, section: {section}")
    page = await get_page_details(db, site, section, page_name)
    logger.info(f"&&&&&&&&&&& Returning with page details: {page.name} {page.primary_image}")
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page

# Get all pages for the given site
@router.get("/pages_all/{site_name}", response_model=list[PageResponse])
async def read_all_pages(site_name: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"read_all_pages called with site: {site_name}")
    return await get_pages_by_site(db, site_name)

# Get page by ID
@router.get("/page_by_id/{page_id}", response_model=PageResponse)
async def read_page_by_id(page_id: int, db: AsyncSession = Depends(get_db)):
    logger.info(f"read_page_by_id called with ID: {page_id}")
    page = await get_page_details_by_id(db, page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page

# Create a new page
@router.post("/pages", response_model=PageCreateResponse)
async def create_new_page(page: PageCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"create_new_page called with {page}")
    return await create_page(db, page)

@router.put("/pages/{page_name}", response_model=PageResponse)
async def update_existing_page(page_name: str, page: PageCreate, db: AsyncSession = Depends(get_db)):
    return await update_page(db, page_name, page)

@router.put("/page_by_id/{page_id}", response_model=PageResponse)
async def update_existing_page_by_id(page_id: int, page: PageCreate, db: AsyncSession = Depends(get_db)):
    return await update_page(db, page_id, page)

@router.delete("/pages/{page_id}")
async def remove_page(page_id: int, db: AsyncSession = Depends(get_db)):
    await delete_page(db, page_id)
    return {"message": "Page deleted successfully"}
