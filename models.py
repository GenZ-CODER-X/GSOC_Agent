from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from db.database import Base


class Organisation_entry(Base):
    __tablename__ = "organisations_entry"
    id = Column(Integer, primary_key=True, index=True)
    org_name = Column(String(255), unique=True, nullable=False)
    source_url_1 = Column(String, unique=True, nullable=True, default=None)
    source_url_2 = Column(String, unique=True, nullable=True, default=None)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    organisation = relationship(
        "Organisation",
        back_populates="user_entry",
        uselist=False,
        cascade="all, delete-orphan",
    )
    discarded_org = relationship(   # NEW — needed for Discard_org's back-reference
        "Discard_org",
        back_populates="user_entry",
        uselist=False,
        cascade="all, delete-orphan",
    )

class Organisation(Base):
    __tablename__ = "organisations"
    id = Column(Integer, primary_key=True, index=True)
    org_name = Column(String(255), unique=True, nullable=False)
    user_entry_id=Column(Integer,ForeignKey("organisations_entry.id"),nullable=False,unique=True)
    status = Column(String(100),default="Pending")
    recent_activity = Column(Text)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    # Relationships
    info_from_sources = relationship(
        "InfoFromSources",
        back_populates="organisation",
        cascade="all, delete-orphan",
    )
    results = relationship(
        "Result",
        back_populates="organisation",
        cascade="all, delete-orphan",
    )
    user_entry = relationship("Organisation_entry", back_populates="organisation")  # DIFFERENT name than the Column above

class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    info_id = Column(
        Integer,
        ForeignKey("info_from_sources.id"),
        nullable=False,
    )
    source_type = Column(
        String(100),
        nullable=False,
    )
    source_url = Column(
        String(1000),
        nullable=False,
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    # Relationship
    info = relationship(
        "InfoFromSources",
        back_populates="sources",
    )
class InfoFromSources(Base):
    __tablename__ = "info_from_sources"
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(
        Integer,
        ForeignKey("organisations.id"),
        nullable=False,
    )
    # Information extracted from the sources
    structured_info = Column(JSON)
    # Raw/unstructured information
    unstructured_info = Column(Text)
    # Additional file that the agent can use
    # for deeper research
    extra_info_file_name = Column(String(500),nullable=False)
    recent_activity = Column(Text)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    # Relationships
    organisation = relationship(
        "Organisation",
        back_populates="info_from_sources",
    )
    sources = relationship(
        "Source",
        back_populates="info",
        cascade="all, delete-orphan",
    )

class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(
        Integer,
        ForeignKey("organisations.id"),
        nullable=False,
    )
    org_name = Column(
        String(255),
        nullable=False,
    )
    alignment_score=Column(Integer,nullable=False)
    # Final synthesized information
    recent_activity = Column(Text)
    # Store structured result data
    tech_stack = Column(JSON)
    projects = Column(JSON)
    mentors = Column(JSON)
    contribution_areas = Column(JSON)
    communication_centers=Column(JSON,nullable=True)
    # Paths to generated/stored research artifacts
    sources_path = Column(String(500))
    info_path = Column(String(500))
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    # Relationship
    organisation = relationship(
        "Organisation",
        back_populates="results",
    )
    
class Discard_org(Base):
    __tablename__ = "discard_orgs"
    id = Column(Integer, primary_key=True)
    org_name = Column(String(255), nullable=False, unique=True)
    user_entry_id = Column(Integer, ForeignKey("organisations_entry.id"), nullable=False, unique=True)
    Tech_stack_org = Column(JSON, nullable=True)  # you said null is fine now
    missing_skills=Column(JSON,nullable=True)
    reason = Column(String, nullable=False)
    user_entry = relationship("Organisation_entry", back_populates="discarded_org")