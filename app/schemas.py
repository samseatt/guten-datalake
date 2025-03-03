from pydantic import BaseModel
from typing import Optional

# Site Schema
class SiteBase(BaseModel):
    name: str
    title: str
    url: str
    logo: str
    favicon: str

class SiteCreate(SiteBase):
    pass

class SiteResponse(SiteBase):
    id: int
    # landing_page_id: int

class SiteUpdate(BaseModel):
    title: str
    url: str
    logo: str
    favicon: str

# Section Schema
class SectionBase(BaseModel):
    site_id: int
    name: str
    title: str

class SectionCreate(BaseModel):
    site_name: str
    name: str
    title: str

class SectionResponse(SectionBase):
    id: int

class SectionUpdate(BaseModel):
    name: str
    title: str
    theme_id: Optional[int] = None

# Page Schema
class PageBase(BaseModel):
    site_name: str
    section_name: str
    name: str
    title: str
    abstract: Optional[str] = None
    content: Optional[str] = None

class PageCreate(PageBase):
    pass

class PageResponse(BaseModel):
    id: int
    section_id: int
    name: str
    title: str
    abstract: Optional[str] = None
    content: Optional[str] = None

# Refs Schema
class RefBase(BaseModel):
    site_name: str
    section_name: str
    page_name: str
    url: str
    # type: str
    description: Optional[str] = None

class RefCreate(RefBase):
    pass

class RefResponse(BaseModel):
    id: int
    page_id: int
    url: str
    # type: str
    description: Optional[str] = None

# Notes Schema
class NoteBase(BaseModel):
    site_name: str
    section_name: str
    page_name: str
    note: str

class NoteCreate(NoteBase):
    pass

class NoteResponse(BaseModel):
    id: int
    page_id: int
    note: str
