from sqlalchemy import (
    Column,
    String,
    Date,
    Integer
)
from datetime import date

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
    created_at = Column(Date, default=date.today())
