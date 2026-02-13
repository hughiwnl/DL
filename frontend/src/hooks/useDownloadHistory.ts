import { useCallback, useEffect, useState } from "react";
import type { DownloadRecord } from "../types";
import { getDownloads, deleteDownload as apiDelete } from "../api/client";

export function useDownloadHistory() {
  const [history, setHistory] = useState<DownloadRecord[]>([]);

  const refresh = useCallback(async () => {
    try {
      const data = await getDownloads();
      setHistory(data);
    } catch {
      // silently fail on history fetch
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const deleteDownload = async (id: string) => {
    await apiDelete(id);
    setHistory((prev) => prev.filter((d) => d.id !== id));
  };

  return { history, refresh, deleteDownload };
}
