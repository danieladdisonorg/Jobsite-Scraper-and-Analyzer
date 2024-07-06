from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer
)
from datetime import datetime

from web_server.db.connnect_db import Base


class DiagramFileMetaData(Base):
    __tablename__ = "DiagramFileMetaData"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(
        String(300),
        unique=True,
        index=True,
        nullable=True
    )
    created_at = Column(DateTime, default=datetime.utcnow)
