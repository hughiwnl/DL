import os

import yt_dlp

from app.schemas import FormatInfo, VideoInfo


def extract_info(url: str) -> VideoInfo:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    formats = []
    seen = set()

    for f in info.get("formats", []):
        if not f.get("url"):
            continue

        has_video = f.get("vcodec", "none") != "none"
        has_audio = f.get("acodec", "none") != "none"

        if has_video:
            height = f.get("height", 0)
            label = f"{height}p" if height else f.get("format_note", "unknown")
        elif has_audio:
            label = "audio only"
        else:
            continue

        dedup_key = (label, f.get("ext"), has_video, has_audio)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        formats.append(
            FormatInfo(
                format_id=f["format_id"],
                ext=f.get("ext", "unknown"),
                quality_label=label,
                filesize_approx=f.get("filesize") or f.get("filesize_approx"),
                has_video=has_video,
                has_audio=has_audio,
                note=f.get("format_note", ""),
            )
        )

    formats.insert(
        0,
        FormatInfo(
            format_id="bestvideo+bestaudio/best",
            ext="mp4",
            quality_label="Best quality",
            filesize_approx=None,
            has_video=True,
            has_audio=True,
            note="Best available video + audio merged",
        ),
    )

    return VideoInfo(
        url=url,
        title=info.get("title", "Unknown"),
        thumbnail=info.get("thumbnail"),
        duration=info.get("duration"),
        uploader=info.get("uploader"),
        formats=formats,
    )


def download_video(
    url: str, format_id: str, output_dir: str, progress_callback
) -> dict:
    ydl_opts = {
        "format": format_id,
        "outtmpl": os.path.join(output_dir, "%(title)s [%(id)s].%(ext)s"),
        "progress_hooks": [progress_callback],
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if not os.path.exists(filename):
            base, _ = os.path.splitext(filename)
            filename = base + ".mp4"
        return {
            "filename": os.path.basename(filename),
            "title": info.get("title"),
            "filesize": os.path.getsize(filename) if os.path.exists(filename) else None,
        }
