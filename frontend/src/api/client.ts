import type { VideoInfo, DownloadRecord } from "../types";

const BASE = "/api";

export async function extractVideoInfo(url: string): Promise<VideoInfo> {
  const res = await fetch(`${BASE}/extract`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Extraction failed" }));
    throw new Error(err.detail || "Extraction failed");
  }
  return res.json();
}

export async function startDownload(
  url: string,
  formatId: string
): Promise<DownloadRecord> {
  const res = await fetch(`${BASE}/downloads`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, format_id: formatId }),
  });
  if (!res.ok) {
    const err = await res
      .json()
      .catch(() => ({ detail: "Download failed to start" }));
    throw new Error(err.detail || "Download failed to start");
  }
  return res.json();
}

export function getFileUrl(id: string): string {
  return `${BASE}/downloads/${id}/file`;
}

export function getProgressUrl(id: string): string {
  return `${BASE}/downloads/${id}/progress`;
}
