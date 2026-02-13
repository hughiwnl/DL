import { useEffect, useRef, useState } from "react";
import type { ProgressEvent } from "../types";
import { getProgressUrl } from "../api/client";

export function useDownloadProgress(downloadId: string | null) {
  const [progress, setProgress] = useState<ProgressEvent | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!downloadId) {
      setProgress(null);
      return;
    }

    const es = new EventSource(getProgressUrl(downloadId));
    eventSourceRef.current = es;

    es.addEventListener("progress", (e) => {
      const data: ProgressEvent = JSON.parse(
        (e as MessageEvent).data
      );
      setProgress(data);

      if (data.status === "completed" || data.status === "failed") {
        es.close();
      }
    });

    es.addEventListener("heartbeat", () => {});

    es.onerror = () => {};

    return () => {
      es.close();
      eventSourceRef.current = null;
    };
  }, [downloadId]);

  return progress;
}
