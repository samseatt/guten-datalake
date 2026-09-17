#!/usr/bin/env python3
"""Publish existing, never-published sites for the initial draft-to-published cutover.

Skips sites with publication history (including deliberately unpublished sites).
Can safely resume after a partial failure; each site is one atomic transaction.
"""
import argparse
import asyncio
from pathlib import Path
import sys
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from app.publication import get_status, publish_site
from app.crud import _site


async def seed(database, allow_master=False):
    if not database.startswith("guten_") or (database == "guten_datalake" and not allow_master):
        raise ValueError("Master requires --allow-master after backup and rehearsal")
    engine = create_async_engine(URL.create("postgresql+asyncpg", database=database))
    try:
        async with AsyncSession(engine, expire_on_commit=False) as db:
            names = (await db.execute(text("SELECT name FROM draft.sites ORDER BY id"))).scalars().all()
        for name in names:
            async with AsyncSession(engine, expire_on_commit=False) as db:
                await _site(db, name=name, lock=True)
                status = await get_status(db, name)
                if status["is_published"] or status["publish_count"]:
                    print(f"Skipped existing publication/history: {name}")
                    continue
                await publish_site(db, name, status["draft_fingerprint"])
                print(f"Published: {name}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", required=True)
    parser.add_argument("--allow-master", action="store_true")
    args = parser.parse_args()
    asyncio.run(seed(args.database, args.allow_master))
