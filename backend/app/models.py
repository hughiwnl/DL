import enum

from sqlalchemy import Column, String, Integer, Float, DateTime, Enum as SAEnum
from sqlalchemy.sql import func

from app.database import Base


class DownloadStatus(str, enum.Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Download(Base):
    __tablename__ = "downloads"

    id = Column(String, primary_key=True)
    url = Column(String, nullable=False)
    title = Column(String, nullable=True)
    thumbnail = Column(String, nullable=True)
    format_id = Column(String, nullable=True)
    quality_label = Column(String, nullable=True)
    filename = Column(String, nullable=True)
    filesize = Column(Integer, nullable=True)
    status = Column(SAEnum(DownloadStatus), default=DownloadStatus.PENDING)
    error_message = Column(String, nullable=True)
    celery_task_id = Column(String, nullable=True)
    progress = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
