export interface FormatInfo {
  format_id: string;
  ext: string;
  quality_label: string;
  filesize_approx: number | null;
  has_video: boolean;
  has_audio: boolean;
  note: string;
}

export interface VideoInfo {
  url: string;
  title: string;
  thumbnail: string | null;
  duration: number | null;
  uploader: string | null;
  formats: FormatInfo[];
}

export interface DownloadRecord {
  id: string;
  url: string;
  title: string | null;
  format_id: string | null;
  filename: string | null;
  filesize: number | null;
  status: "pending" | "downloading" | "processing" | "completed" | "failed";
  progress: number;
  error_message: string | null;
}

export interface ProgressEvent {
  status: string;
  progress: number;
  downloaded_bytes?: number;
  total_bytes?: number;
  speed?: number;
  eta?: number;
  error?: string;
  filename?: string;
}
