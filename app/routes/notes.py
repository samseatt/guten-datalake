from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud import get_notes_by_page, create_note, update_note, delete_note
from app.schemas import NoteCreate, NoteUpdate, NoteResponse

router = APIRouter()


@router.get("/notes", response_model=list[NoteResponse])
async def read_notes(site: str, section: str, page: str, db: AsyncSession = Depends(get_db)):
    return await get_notes_by_page(db, site, section, page)


@router.post("/notes", response_model=NoteResponse)
async def create_new_note(data: NoteCreate, db: AsyncSession = Depends(get_db)):
    return await create_note(db, data)


@router.put("/notes/{item_id}", response_model=NoteResponse)
async def update_existing_note(item_id: int, data: NoteUpdate, db: AsyncSession = Depends(get_db)):
    return await update_note(db, item_id, data)


@router.delete("/notes/{item_id}")
async def remove_note(item_id: int, site: str, section: str, page: str, db: AsyncSession = Depends(get_db)):
    await delete_note(db, item_id, site, section, page)
    return {"message": "Note deleted successfully"}
