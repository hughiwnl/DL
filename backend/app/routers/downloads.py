import asyncio
import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from starlette.background import BackgroundTask
from starlette.responses import FileResponse

from app.config import settings
from app.schemas import (
    DownloadResponse,
    ExtractRequest,
    StartDownloadRequest,
    VideoInfo,
)
from app.services import ytdlp_service
from app.tasks.download_task import download_video_task
from app.utils.progress import get_job, set_job, delete_job

router = APIRouter(prefix="/api")


@router.post("/extract", response_model=VideoInfo)
async def extract_video_info(req: ExtractRequest):
    try:
        info = await asyncio.to_thread(ytdlp_service.extract_info, str(req.url))
        return info
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e)[:500])


@router.post("/downloads", response_model=DownloadResponse, status_code=201)
async def start_download(req: StartDownloadRequest):
    download_id = str(uuid4())

    job = {
        "id": download_id,
        "url": str(req.url),
        "format_id": req.format_id,
        "status": "pending",
        "progress": 0.0,
        "title": None,
        "filename": None,
        "filesize": None,
        "error_message": None,
    }
    set_job(download_id, job)

    task = download_video_task.delay(download_id, str(req.url), req.format_id)
    job["celery_task_id"] = task.id
    set_job(download_id, job)

    return DownloadResponse(**job)


@router.get("/downloads/{download_id}", response_model=DownloadResponse)
async def get_download(download_id: str):
    job = get_job(download_id)
    if not job:
        raise HTTPException(status_code=404, detail="Download not found or expired")
    return DownloadResponse(**job)


@router.get("/downloads/{download_id}/file")
async def serve_file(download_id: str):
    job = get_job(download_id)
    if not job or job.get("status") != "completed" or not job.get("filename"):
        raise HTTPException(status_code=404, detail="File not available")

    filepath = Path(settings.DOWNLOADS_DIR) / job["filename"]
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File no longer exists")

    def cleanup():
        try:
            if os.path.exists(str(filepath)):
                os.remove(str(filepath))
            delete_job(download_id)
        except OSError:
            pass

    return FileResponse(
        path=str(filepath),
        filename=job["filename"],
        media_type="application/octet-stream",
        background=BackgroundTask(cleanup),
    )
