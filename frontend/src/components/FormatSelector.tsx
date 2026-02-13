import type { FormatInfo } from "../types";

interface Props {
  formats: FormatInfo[];
  selected: string | null;
  onSelect: (formatId: string) => void;
}

function formatFileSize(bytes: number | null): string {
  if (!bytes) return "";
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  if (bytes < 1024 * 1024 * 1024)
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
}

export function FormatSelector({ formats, selected, onSelect }: Props) {
  const videoFormats = formats.filter((f) => f.has_video);
  const audioFormats = formats.filter((f) => !f.has_video && f.has_audio);

  return (
    <div className="format-selector">
      <h4>Select Format</h4>

      {videoFormats.length > 0 && (
        <div className="format-group">
          <label className="format-group-label">Video</label>
          {videoFormats.map((f) => (
            <button
              key={f.format_id}
              className={`format-option ${selected === f.format_id ? "selected" : ""}`}
              onClick={() => onSelect(f.format_id)}
            >
              <span className="format-quality">{f.quality_label}</span>
              <span className="format-ext">{f.ext}</span>
              {f.filesize_approx && (
                <span className="format-size">
                  {formatFileSize(f.filesize_approx)}
                </span>
              )}
            </button>
          ))}
        </div>
      )}

      {audioFormats.length > 0 && (
        <div className="format-group">
          <label className="format-group-label">Audio Only</label>
          {audioFormats.map((f) => (
            <button
              key={f.format_id}
              className={`format-option ${selected === f.format_id ? "selected" : ""}`}
              onClick={() => onSelect(f.format_id)}
            >
              <span className="format-quality">{f.quality_label}</span>
              <span className="format-ext">{f.ext}</span>
              {f.filesize_approx && (
                <span className="format-size">
                  {formatFileSize(f.filesize_approx)}
                </span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
