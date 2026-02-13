import time

from sqlalchemy.sql import func

from app.tasks.celery_app import celery_app
from app.services.ytdlp_service import download_video
from app.database import SessionLocal
from app.models import Download, DownloadStatus
from app.utils.progress import set_progress
from app.config import settings


@celery_app.task(bind=True, name="download_video")
def download_video_task(self, download_id: str, url: str, format_id: str):
    db = SessionLocal()
    last_update = 0

    try:
        download = db.query(Download).filter(Download.id == download_id).first()
        download.status = DownloadStatus.DOWNLOADING
        db.commit()

        def progress_callback(d):
            nonlocal last_update
            now = time.time()

            if d["status"] == "downloading":
                if now - last_update < 0.5:
                    return
                last_update = now

                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded = d.get("downloaded_bytes", 0)
                pct = (downloaded / total * 100) if total > 0 else 0

                set_progress(download_id, {
                    "status": "downloading",
                    "progress": round(pct, 1),
                    "downloaded_bytes": downloaded,
                    "total_bytes": total,
                    "speed": d.get("speed", 0),
                    "eta": d.get("eta", 0),
                })

            elif d["status"] == "finished":
                set_progress(download_id, {
                    "status": "processing",
                    "progress": 99.0,
                })

        result = download_video(
            url, format_id, settings.DOWNLOADS_DIR, progress_callback
        )

        download.status = DownloadStatus.COMPLETED
        download.filename = result["filename"]
        download.title = result.get("title") or download.title
        download.filesize = result.get("filesize")
        download.progress = 100.0
        download.completed_at = func.now()
        db.commit()

        set_progress(download_id, {
            "status": "completed",
            "progress": 100.0,
            "filename": result["filename"],
        })

        return {"download_id": download_id, "filename": result["filename"]}

    except Exception as e:
        download = db.query(Download).filter(Download.id == download_id).first()
        if download:
            download.status = DownloadStatus.FAILED
            download.error_message = str(e)[:500]
            db.commit()

        set_progress(download_id, {
            "status": "failed",
            "progress": 0,
            "error": str(e)[:500],
        })
        raise

    finally:
        db.close()
