from fastapi import FastAPI
from app.routes import sites, sections, pages, refs, notes, publish
from utils.logging import setup_logging

# Set up logging for the application
setup_logging(log_level="DEBUG", log_file="logs/guten_datalake.log")

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
