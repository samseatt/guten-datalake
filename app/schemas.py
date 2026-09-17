from pydantic import BaseModel, ConfigDict, StrictInt, HttpUrl, TypeAdapter, field_validator
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
    model_config = ConfigDict(from_attributes=True)
    id: int
    sort_order: int

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
    model_config = ConfigDict(from_attributes=True)
    id: int
    sort_order: int
    section_name: Optional[str] = None
    section_id: int
    # section_name: str
    name: str
    title: str
    primary_image: Optional[str] = None
    abstract: Optional[str] = None
    content: Optional[str] = None

class PageCreateResponse(BaseModel):
    id: int
    sort_order: int
    section_id: int
    # section_id: int
    section_name: str
    name: str
    title: str
    primary_image: Optional[str] = None
    abstract: Optional[str] = None
    content: Optional[str] = None

# Editorial attachments are always addressed within their owning page.
class PageScope(BaseModel):
    site_name: str
    section_name: str
    page_name: str

class RefBase(PageScope):
    url: str
    description: Optional[str] = None

    @field_validator("url")
    @classmethod
    def valid_url(cls, value):
        value = value.strip()
        if len(value) > 255:
            raise ValueError("Reference URL must be at most 255 characters")
        TypeAdapter(HttpUrl).validate_python(value)
        return value

class RefCreate(RefBase):
    pass

class RefUpdate(RefBase):
    pass

class RefResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    page_id: int
    url: str
    description: Optional[str] = None

class NoteBase(PageScope):
    note: str

    @field_validator("note")
    @classmethod
    def nonempty_note(cls, value):
        if not value.strip():
            raise ValueError("Note must not be empty")
        return value

class NoteCreate(NoteBase):
    pass

class NoteUpdate(NoteBase):
    pass

class NoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    page_id: int
    note: str


class OrderRequest(BaseModel):
    ids: list[StrictInt]
    expected_ids: list[StrictInt]

    @field_validator("ids", "expected_ids")
    @classmethod
    def valid_ids(cls, ids):
        if len(ids) != len(set(ids)) or any(value <= 0 for value in ids):
            raise ValueError("IDs must be positive and contain no duplicates")
        return ids


class LandingResponse(BaseModel):
    section_name: str
    page_name: str


class PublicationRequest(BaseModel):
    expected_fingerprint: str

    @field_validator("expected_fingerprint")
    @classmethod
    def valid_fingerprint(cls, value):
        if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
            raise ValueError("Expected a SHA-256 publication fingerprint")
        return value


class PublishedPageBundle(BaseModel):
    site: SiteResponse
    section: SectionResponse
    page: PageResponse
    sections: list[SectionResponse]
    pages: list[PageResponse]
