from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud import (
    get_refs_by_page, create_ref
    # , get_ref_details, create_ref,
    # update_ref, delete_ref
)
from app.schemas import RefCreate, RefResponse
import logging

# Logger for this file
logger = logging.getLogger(__name__)

router = APIRouter()

# Get all references for a page
@router.get("/refs", response_model=list[RefResponse])
async def read_refs(site: str, section: str, page: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"@@@@@@@@@@@@@@ read_refs called with site: {site}, section: {section}, page: {page}")
    return await get_refs_by_page(db, site, section, page)

# Create a new ref
@router.post("/refs", response_model=RefResponse)
async def create_new_ref(ref: RefCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"@@@@@@@@@@@@@@ create_new_ref called with {ref}")
    return await create_ref(db, ref)

