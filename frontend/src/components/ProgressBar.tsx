interface Props {
  progress: number;
  status: string;
}

export function ProgressBar({ progress, status }: Props) {
  return (
    <div className="progress-bar-container">
      <div className="progress-bar">
        <div
          className={`progress-bar-fill ${status}`}
          style={{ width: `${Math.min(progress, 100)}%` }}
        />
      </div>
      <span className="progress-text">{progress.toFixed(1)}%</span>
    </div>
  );
}
