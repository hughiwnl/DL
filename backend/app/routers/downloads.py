import asyncio
import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from app.config import settings
from app.database import get_db
from app.models import Download, DownloadStatus
from app.schemas import (
    DownloadResponse,
    ExtractRequest,
    StartDownloadRequest,
    VideoInfo,
)
from app.services import ytdlp_service
from app.tasks.download_task import download_video_task

router = APIRouter(prefix="/api")


@router.post("/extract", response_model=VideoInfo)
async def extract_video_info(req: ExtractRequest):
    try:
        info = await asyncio.to_thread(ytdlp_service.extract_info, str(req.url))
        return info
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e)[:500])


@router.post("/downloads", response_model=DownloadResponse, status_code=201)
async def start_download(req: StartDownloadRequest, db: Session = Depends(get_db)):
    download_id = str(uuid4())

    download = Download(
        id=download_id,
        url=str(req.url),
        format_id=req.format_id,
        status=DownloadStatus.PENDING,
        progress=0.0,
    )
    db.add(download)
    db.commit()

    task = download_video_task.delay(download_id, str(req.url), req.format_id)

    download.celery_task_id = task.id
    db.commit()
    db.refresh(download)

    return _to_response(download)


@router.get("/downloads", response_model=list[DownloadResponse])
async def list_downloads(db: Session = Depends(get_db)):
    downloads = (
        db.query(Download).order_by(Download.created_at.desc()).limit(50).all()
    )
    return [_to_response(d) for d in downloads]


@router.get("/downloads/{download_id}", response_model=DownloadResponse)
async def get_download(download_id: str, db: Session = Depends(get_db)):
    download = db.query(Download).filter(Download.id == download_id).first()
    if not download:
        raise HTTPException(status_code=404, detail="Download not found")
    return _to_response(download)


@router.delete("/downloads/{download_id}", status_code=204)
async def delete_download(download_id: str, db: Session = Depends(get_db)):
    download = db.query(Download).filter(Download.id == download_id).first()
    if not download:
        raise HTTPException(status_code=404, detail="Download not found")

    if download.filename:
        filepath = Path(settings.DOWNLOADS_DIR) / download.filename
        if filepath.exists():
            os.remove(filepath)

    db.delete(download)
    db.commit()


@router.get("/downloads/{download_id}/file")
async def serve_file(download_id: str, db: Session = Depends(get_db)):
    download = db.query(Download).filter(Download.id == download_id).first()
    if not download or download.status != DownloadStatus.COMPLETED:
        raise HTTPException(status_code=404, detail="File not available")

    filepath = Path(settings.DOWNLOADS_DIR) / download.filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File no longer exists on disk")

    return FileResponse(
        path=str(filepath),
        filename=download.filename,
        media_type="application/octet-stream",
    )


def _to_response(download: Download) -> DownloadResponse:
    return DownloadResponse(
        id=download.id,
        url=download.url,
        title=download.title,
        thumbnail=download.thumbnail,
        format_id=download.format_id,
        quality_label=download.quality_label,
        filename=download.filename,
        filesize=download.filesize,
        status=download.status.value if download.status else "pending",
        progress=download.progress or 0.0,
        error_message=download.error_message,
        created_at=str(download.created_at) if download.created_at else "",
        completed_at=str(download.completed_at) if download.completed_at else None,
    )
