export default function PriorityBadge({ priority }) {

  const normalized =
    priority || "UNKNOWN";

  return (
    <span
      className={`priority-badge ${normalized.toLowerCase()}`}
    >
      <span className="priority-dot" />
      {normalized}
    </span>
  );
}
