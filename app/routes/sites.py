from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
import app.crud as crud
from app.crud import create_site, get_site_by_name, get_sites
from app.schemas import SiteCreate, SiteResponse, SiteUpdate
import logging

# Logger for this file
logger = logging.getLogger(__name__)

router = APIRouter()

# @router.get("/sites")
# async def read_sites(db: AsyncSession = Depends(get_db)):
#     logger.info(f"$$$$$$$$$$$ read_sites called")
#     return await get_sites(db)

# @router.get("/sites/{site_name}")
# async def read_site(site_name: str, db: AsyncSession = Depends(get_db)):
#     return await get_site_by_name(db, site_name)

@router.get("/sites", response_model=list[SiteResponse])
async def read_sites(db: AsyncSession = Depends(get_db)):
    return await get_sites(db)

@router.get("/sites/{site_name}", response_model=SiteResponse)
async def read_site(site_name: str, db: AsyncSession = Depends(get_db)):
    site = await get_site_by_name(db, site_name)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site

@router.post("/sites", response_model=SiteResponse)
async def create_new_site(site: SiteCreate, db: AsyncSession = Depends(get_db)):
    new_site = await create_site(db, site)
    return new_site

@router.put("/sites/{site_name}")
async def update_site(site_name: str, site: SiteUpdate, db: AsyncSession = Depends(get_db)):
    logger.info(f"$$$$$$$$$$$ update_site called with site_name: {site_name}")
    updated_site = await crud.update_site(db, site_name, site)
    logger.info(f"$$$$$$$$$$$ update_site returned {update_site}")
    if not updated_site:
        raise HTTPException(status_code=404, detail="Site not found")
    return updated_site

# @router.put("/sites/{site_name}", response_model=PageResponse)
# async def update_existing_site(page_id: int, page: PageCreate, db: AsyncSession = Depends(get_db)):
#     return await update_site(db, page_id, page)

@router.delete("/site/{site_name}")
async def delete_site(site_name: str, db: AsyncSession = Depends(get_db)):
    deleted = await crud.delete_site(db, site_name)
    if not deleted:
        raise HTTPException(status_code=404, detail="Site not found")
    return {"detail": "Site deleted"}

# @router.delete("/sites/{site_name}")
# async def remove_page(page_id: int, db: AsyncSession = Depends(get_db)):
#     await delete_site(db, page_id)
#     return {"message": "Page deleted successfully"}
