from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Define Site Table in Draft Schema
class Site(Base):
    __tablename__ = "sites"
    __table_args__ = {"schema": "draft"}  # Use draft schema for site editing

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    logo = Column(String, nullable=False)
    favicon = Column(String, nullable=True)
    color = Column(String, nullable=True)
    landing_page_id = Column(Integer, nullable=True)

# Define Section Table in Draft Schema
class Section(Base):
    __tablename__ = "sections"
    __table_args__ = {"schema": "draft"}

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("draft.sites.id"), nullable=False)
    name = Column(String, index=True)
    title = Column(String, nullable=False)
    label = Column(String, nullable=True)

# Define Page Table in Draft Schema
class Page(Base):
    __tablename__ = "pages"
    __table_args__ = {"schema": "draft"}

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("draft.sections.id"), nullable=False)
    name = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    primary_image = Column(String, nullable=True)
    abstract = Column(Text)
    content = Column(Text)

# Published Site Model
class PublishedSite(Base):
    __tablename__ = "sites"
    __table_args__ = {"schema": "published"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)

# Published Page Model
class PublishedPage(Base):
    __tablename__ = "pages"
    __table_args__ = {"schema": "published"}

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("published.sections.id"), nullable=False)
    name = Column(String, unique=True, index=True)
    title = Column(String, nullable=False)
    abstract = Column(Text)
    content = Column(Text)

# Define Ref Table in Draft Schema
class Ref(Base):
    __tablename__ = "refs"
    __table_args__ = {"schema": "draft"}

    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("draft.pages.id"), nullable=False)
    url = Column(String, index=True)
    description = Column(String, nullable=False)
    type = Column(String, nullable=False)

# Define Note Table in Draft Schema
class Note(Base):
    __tablename__ = "notes"
    __table_args__ = {"schema": "draft"}

    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("draft.pages.id"), nullable=False)
    note = Column(Text)
