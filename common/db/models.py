import enum
from sqlalchemy import (
    Column,
    String,
    Date,
    Integer,
    Enum
)
from datetime import date

from common.db.connnect_db import Base


class DiagramTypes(enum.Enum):
    employment_type = "Employment type"
    location = "Location"
    optional_skills = "Optional skills"
    required_skills = "Required skills"
    o_s = "OS"
    skills_by_level_of_exp = "Skills by level of experience"
    ua_support = "UA support"


class BaseFileMetaData:
    id = Column(Integer, primary_key=True)
    file_name = Column(
        String(300),
        unique=True,
        index=True,
        nullable=True
    )
    created_at = Column(Date, default=date.today())


class DiagramFileMetaData(Base, BaseFileMetaData):
    """Model for saving the results of scraping in jupyter file"""
    __tablename__ = "diagram_file_meta_data"

    diagram_type = Column(Enum(DiagramTypes), nullable=False, index=True)


class ScrapingResultFileMetaData(Base, BaseFileMetaData):
    """Model for saving metadata of scraping result"""
    __tablename__ = "scraping_result_file_meta_data"
