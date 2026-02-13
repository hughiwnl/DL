from pydantic import BaseModel, HttpUrl
from typing import Optional


class ExtractRequest(BaseModel):
    url: HttpUrl


class StartDownloadRequest(BaseModel):
    url: HttpUrl
    format_id: str


class FormatInfo(BaseModel):
    format_id: str
    ext: str
    quality_label: str
    filesize_approx: Optional[int] = None
    has_video: bool
    has_audio: bool
    note: str


class VideoInfo(BaseModel):
    url: str
    title: str
    thumbnail: Optional[str] = None
    duration: Optional[int] = None
    uploader: Optional[str] = None
    formats: list[FormatInfo]


class DownloadResponse(BaseModel):
    id: str
    url: str
    title: Optional[str] = None
    thumbnail: Optional[str] = None
    format_id: Optional[str] = None
    quality_label: Optional[str] = None
    filename: Optional[str] = None
    filesize: Optional[int] = None
    status: str
    progress: float
    error_message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None

    class Config:
        from_attributes = True
