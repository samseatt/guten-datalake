from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud import get_refs_by_page, create_ref, update_ref, delete_ref
from app.schemas import RefCreate, RefUpdate, RefResponse

router = APIRouter()


@router.get("/refs", response_model=list[RefResponse])
async def read_refs(site: str, section: str, page: str, db: AsyncSession = Depends(get_db)):
    return await get_refs_by_page(db, site, section, page)


@router.post("/refs", response_model=RefResponse)
async def create_new_ref(data: RefCreate, db: AsyncSession = Depends(get_db)):
    return await create_ref(db, data)


@router.put("/refs/{item_id}", response_model=RefResponse)
async def update_existing_ref(item_id: int, data: RefUpdate, db: AsyncSession = Depends(get_db)):
    return await update_ref(db, item_id, data)


@router.delete("/refs/{item_id}")
async def remove_ref(item_id: int, site: str, section: str, page: str, db: AsyncSession = Depends(get_db)):
    await delete_ref(db, item_id, site, section, page)
    return {"message": "Ref deleted successfully"}
