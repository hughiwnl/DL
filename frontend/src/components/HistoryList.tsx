import type { DownloadRecord } from "../types";
import { DownloadCard } from "./DownloadCard";

interface Props {
  downloads: DownloadRecord[];
  onDelete: (id: string) => void;
}

export function HistoryList({ downloads, onDelete }: Props) {
  if (downloads.length === 0) return null;

  return (
    <div className="history-list">
      <h3>Download History</h3>
      {downloads.map((d) => (
        <DownloadCard key={d.id} download={d} onDelete={onDelete} />
      ))}
    </div>
  );
}
