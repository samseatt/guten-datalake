from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud import publish_site, get_published_page
from app.schemas import PageResponse
import logging

# Logger for this file
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/publish/{site_name}")
async def publish_site_route(site_name: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"^^^^^^^^^^^^^^^ publish_site_route called for site: {site_name}")
    await publish_site(db, site_name)
    return {"message": f"Site '{site_name}' successfully published."}

@router.get("/published/pages/{page_name}", response_model=PageResponse)
async def get_published_page_route(page_name: str, site: str, db: AsyncSession = Depends(get_db)):
    page = await get_published_page(db, site, page_name)
    if not page:
        raise HTTPException(status_code=404, detail="Published page not found")
    return page
