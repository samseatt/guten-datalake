from pydantic import BaseModel
from typing import Optional

# Site Schema
class SiteBase(BaseModel):
    name: str
    title: str
    url: str
    logo: str
    favicon: str
    color: str
    landing_page_id: Optional[int] = None

class SiteCreate(SiteBase):
    pass

class SiteResponse(SiteBase):
    id: int

class SiteUpdate(BaseModel):
    title: str
    url: str
    logo: str
    favicon: str
    color: str
    landing_page_id: Optional[int] = None

# Section Schema
class SectionBase(BaseModel):
    site_id: int
    name: str
    title: str
    label: Optional[str] = None

class SectionCreate(BaseModel):
    site_name: str
    name: str
    title: str
    label: Optional[str] = None

class SectionResponse(SectionBase):
    id: int

class SectionUpdate(BaseModel):
    name: str
    title: str
    label: Optional[str] = None
    theme_id: Optional[int] = None

# Page Schema
class PageBase(BaseModel):
    site_name: str
    section_name: str
    name: str
    title: str
    primary_image: Optional[str] = None
    abstract: Optional[str] = None
    content: Optional[str] = None

class PageCreate(PageBase):
    pass

class PageResponse(BaseModel):
    id: int
    section_id: int
    # section_name: str
    name: str
    title: str
    primary_image: Optional[str] = None
    abstract: Optional[str] = None
    content: Optional[str] = None

class PageCreateResponse(BaseModel):
    id: int
    # section_id: int
    section_name: str
    name: str
    title: str
    primary_image: Optional[str] = None
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

class RefUpdate(RefBase):
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
