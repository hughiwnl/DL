import { useState } from "react";

interface Props {
  onSubmit: (url: string) => void;
  loading: boolean;
}

export function UrlInput({ onSubmit, loading }: Props) {
  const [url, setUrl] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      onSubmit(url.trim());
    }
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setUrl(text);
    } catch {
      // clipboard access denied
    }
  };

  return (
    <form className="url-input" onSubmit={handleSubmit}>
      <div className="url-input-row">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Paste a video URL here..."
          disabled={loading}
        />
        <button
          type="button"
          onClick={handlePaste}
          className="btn-secondary"
          disabled={loading}
        >
          Paste
        </button>
        <button type="submit" className="btn-primary" disabled={loading || !url.trim()}>
          {loading ? "Extracting..." : "Get Video"}
        </button>
      </div>
    </form>
  );
}
