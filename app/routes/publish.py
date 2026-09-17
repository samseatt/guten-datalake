from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import publication
from app.schemas import PublicationRequest, PublishedPageBundle, LandingResponse, PageResponse

router = APIRouter()


async def command(db, operation, *args):
    try:
        return await operation(db, *args)
    except SQLAlchemyError as exc:
        await db.rollback()
        raise HTTPException(503, "Publication could not be completed. The previous published content is unchanged; refresh status before retrying.") from exc


@router.get("/publication-status")
async def statuses(db: AsyncSession = Depends(get_db)):
    return await publication.all_statuses(db)


@router.get("/sites/{site_name}/publication")
async def status(site_name: str, db: AsyncSession = Depends(get_db)):
    return await publication.get_status(db, site_name)


@router.post("/publish/{site_name}")
async def publish(site_name: str, request: PublicationRequest, db: AsyncSession = Depends(get_db)):
    return await command(db, publication.publish_site, site_name, request.expected_fingerprint)


@router.delete("/sites/{site_name}/publication")
async def unpublish(site_name: str, request: PublicationRequest, db: AsyncSession = Depends(get_db)):
    return await command(db, publication.unpublish_site, site_name, request.expected_fingerprint)


@router.get("/published/sites/{site_name}/landing", response_model=LandingResponse)
async def landing(site_name: str, section: str | None = None, db: AsyncSession = Depends(get_db)):
    return await publication.published_landing(db, site_name, section)


@router.get("/published/sites/{site_name}/page", response_model=PublishedPageBundle)
async def page_bundle(site_name: str, section: str, page: str, db: AsyncSession = Depends(get_db)):
    return await publication.published_page(db, site_name, section, page)


@router.get("/published/pages/{page_name}", response_model=PageResponse)
async def page(page_name: str, site: str, section: str, db: AsyncSession = Depends(get_db)):
    return (await publication.published_page(db, site, section, page_name))["page"]
