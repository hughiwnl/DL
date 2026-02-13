import type { VideoInfo } from "../types";

interface Props {
  video: VideoInfo;
}

function formatDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) {
    return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  }
  return `${m}:${String(s).padStart(2, "0")}`;
}

export function VideoPreview({ video }: Props) {
  return (
    <div className="video-preview">
      {video.thumbnail && (
        <img
          src={video.thumbnail}
          alt={video.title}
          className="video-thumbnail"
        />
      )}
      <div className="video-details">
        <h3 className="video-title">{video.title}</h3>
        {video.uploader && (
          <p className="video-uploader">{video.uploader}</p>
        )}
        {video.duration && (
          <p className="video-duration">{formatDuration(video.duration)}</p>
        )}
      </div>
    </div>
  );
}
