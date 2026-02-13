import { useState } from "react";
import type { VideoInfo } from "../types";
import { extractVideoInfo } from "../api/client";

export function useVideoInfo() {
  const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const extract = async (url: string) => {
    setLoading(true);
    setError(null);
    setVideoInfo(null);
    try {
      const info = await extractVideoInfo(url);
      setVideoInfo(info);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to extract video info");
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setVideoInfo(null);
    setError(null);
  };

  return { videoInfo, loading, error, extract, reset };
}
