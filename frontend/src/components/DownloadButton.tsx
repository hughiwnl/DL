interface Props {
  onClick: () => void;
  disabled: boolean;
  loading: boolean;
}

export function DownloadButton({ onClick, disabled, loading }: Props) {
  return (
    <button
      className="btn-primary btn-download"
      onClick={onClick}
      disabled={disabled || loading}
    >
      {loading ? "Starting..." : "Download"}
    </button>
  );
}
