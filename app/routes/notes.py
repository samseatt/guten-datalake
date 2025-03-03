from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud import (
    get_notes_by_page, create_note
    # , get_ref_details, create_ref,
    # update_ref, delete_ref
)
from app.schemas import NoteCreate, NoteResponse
import logging

# Logger for this file
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/notes", response_model=list[NoteResponse])
async def read_notes(site: str, section: str, page: str, db: AsyncSession = Depends(get_db)):
    logger.info(f"@@@@@@@@@@@@@@ read_notes called with site: {site}, section: {section}, page: {page}")
    return await get_notes_by_page(db, site, section, page)

# Create a new note
@router.post("/notes", response_model=NoteResponse)
async def create_new_note(note: NoteCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"@@@@@@@@@@@@@@ create_new_note called with {note}")
    return await create_note(db, note)

