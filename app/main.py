from fastapi import FastAPI
from app.routes import sites, sections, pages, refs, notes, publish
from utils.logging import setup_logging

# Set up logging for the application
setup_logging()

app = FastAPI()

# app.include_router(sites.router, prefix="/guten", tags=["Sites"])
# app.include_router(pages.router, prefix="/guten", tags=["Pages"])
app.include_router(sites.router, prefix="/guten", tags=["Sites"])
app.include_router(sections.router, prefix="/guten", tags=["Sections"])
app.include_router(pages.router, prefix="/guten", tags=["Pages"])
app.include_router(refs.router, prefix="/guten", tags=["Refs"])
app.include_router(notes.router, prefix="/guten", tags=["Notes"])
app.include_router(publish.router, prefix="/guten", tags=["Publishing"])

@app.get("/")
async def root():
    return {"message": "Welcome to guten-datalake API"}


@app.get("/health/live", include_in_schema=False)
async def health_live():
    return {"status": "alive"}


@app.get("/health/ready", include_in_schema=False)
async def health_ready():
    import asyncio
    import hashlib
    from pathlib import Path
    from fastapi.responses import JSONResponse
    from sqlalchemy import text
    from app.database import SessionLocal

    async def check():
        expected = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in (Path(__file__).resolve().parents[1] / "scripts/database/migrations").glob("*.sql")}
        async with SessionLocal() as db:
            applied = dict((await db.execute(text("SELECT version,sha256 FROM workflow.schema_migrations"))).all())
            return bool(expected) and applied == expected
    try:
        if await asyncio.wait_for(check(), timeout=3):
            return {"status": "ready"}
    except Exception:
        pass
    return JSONResponse(status_code=503, content={"status": "not ready"})
