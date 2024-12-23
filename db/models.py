import os
import dotenv
from sqlalchemy import (
    Column,
    String,
    Date,
    Integer,
    func
)
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import date

from db.connnect_db import Base

dotenv.load_dotenv()


class ScrapingResultFileMetaData(Base):
    """Model for saving metadata of scraping result"""
    __tablename__ = "scraping_result_file_meta_data"
    __table_args__ = (
        {"info": {
            "default_order_by": ["created_at"]
        }}
    )

    id = Column(Integer, primary_key=True)
    file_name = Column(
        String(300),
        unique=True,
        index=True,
        nullable=True
    )
    created_at = Column(Date, default=date.today())

    @hybrid_property
    def file_path(self):
        file_path = os.path.join(
            os.getenv("SCRAPING_RESULT_DIR"),
            self.file_name
        )
        if os.path.exists(file_path):
            return file_path
        return FileNotFoundError(f"File does not exist: {file_path}")

    @file_path.expression
    def file_path(cls):
        """Enable 'file_path' to be used in querying"""
        return func.concat(
            os.getenv("SCRAPING_RESULT_DIR"), "/", cls.file_name
        )
