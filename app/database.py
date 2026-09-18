from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
import ssl
from dotenv import load_dotenv

from pathlib import Path
from sqlalchemy.engine import make_url

# Load this service's local settings without overriding explicitly supplied test/deploy settings.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
database_url_file = os.environ.get("DATABASE_URL_FILE", "").strip()
if DATABASE_URL and database_url_file:
    raise RuntimeError("Set DATABASE_URL or DATABASE_URL_FILE, not both.")
if database_url_file:
    try:
        DATABASE_URL = Path(database_url_file).read_text().strip()
    except OSError:
        raise RuntimeError("Could not read DATABASE_URL_FILE.") from None
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is required; configure the Datalake environment before starting it.")
try:
    parsed_url = make_url(DATABASE_URL)
    if parsed_url.drivername != "postgresql+asyncpg" or not parsed_url.database:
        raise ValueError()
except Exception:
    raise RuntimeError("DATABASE_URL must identify a PostgreSQL database using postgresql+asyncpg.") from None

# Cloud connections require both CA validation and hostname/IP verification.
# An explicit CA also prevents URL options from silently overriding TLS policy.
connect_args = {}
ca_file = os.environ.get("DATABASE_SSL_CA_FILE", "").strip()
if ca_file:
    if any(key.lower().startswith("ssl") for key in parsed_url.query):
        raise RuntimeError("DATABASE_SSL_CA_FILE cannot be combined with SSL URL options.")
    try:
        context = ssl.create_default_context(cafile=ca_file)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        connect_args["ssl"] = context
    except (OSError, ssl.SSLError):
        raise RuntimeError("Could not load DATABASE_SSL_CA_FILE.") from None

engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    hide_parameters=True,
    pool_pre_ping=True,
    connect_args=connect_args,
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
