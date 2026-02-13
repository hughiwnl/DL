import type { DownloadRecord, ProgressEvent } from "../types";
import { ProgressBar } from "./ProgressBar";
import { getFileUrl } from "../api/client";

interface Props {
  download: DownloadRecord;
  progress?: ProgressEvent | null;
}

function formatSpeed(bytesPerSec: number | undefined): string {
  if (!bytesPerSec) return "";
  if (bytesPerSec < 1024 * 1024)
    return `${(bytesPerSec / 1024).toFixed(0)} KB/s`;
  return `${(bytesPerSec / (1024 * 1024)).toFixed(1)} MB/s`;
}

function formatEta(seconds: number | undefined): string {
  if (!seconds) return "";
  if (seconds < 60) return `${Math.round(seconds)}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`;
  return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
}

export function DownloadCard({ download, progress }: Props) {
  const isActive =
    download.status === "downloading" ||
    download.status === "processing" ||
    download.status === "pending";

  const currentProgress = progress?.progress ?? download.progress;
  const currentStatus = progress?.status ?? download.status;

  return (
    <div className={`download-card ${currentStatus}`}>
      <div className="download-card-header">
        <div className="download-card-info">
          <h4 className="download-card-title">
            {download.title || "Downloading..."}
          </h4>
          <div className="download-card-meta">
            <span className={`status-badge ${currentStatus}`}>
              {currentStatus}
            </span>
          </div>
        </div>
      </div>

      {isActive && (
        <div className="download-card-progress">
          <ProgressBar progress={currentProgress} status={currentStatus} />
          {progress && (
            <div className="progress-details">
              {progress.speed ? (
                <span>{formatSpeed(progress.speed)}</span>
              ) : null}
              {progress.eta ? (
                <span>ETA: {formatEta(progress.eta)}</span>
              ) : null}
            </div>
          )}
        </div>
      )}

      {currentStatus === "completed" && (
        <div className="download-card-actions">
          <a
            href={getFileUrl(download.id)}
            download
            className="btn-primary btn-save"
          >
            Save to PC
          </a>
        </div>
      )}

      {currentStatus === "failed" && download.error_message && (
        <p className="download-error">{download.error_message}</p>
      )}
    </div>
  );
}
