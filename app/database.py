from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

from pathlib import Path
from sqlalchemy.engine import make_url

# Load this service's local settings without overriding explicitly supplied test/deploy settings.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is required; configure the Datalake environment before starting it.")
try:
    parsed_url = make_url(DATABASE_URL)
    if parsed_url.drivername != "postgresql+asyncpg" or not parsed_url.database:
        raise ValueError()
except Exception:
    raise RuntimeError("DATABASE_URL must identify a PostgreSQL database using postgresql+asyncpg.") from None

engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    hide_parameters=True,
    pool_pre_ping=True,
)

# Create async session factory
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Dependency to get DB session
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
