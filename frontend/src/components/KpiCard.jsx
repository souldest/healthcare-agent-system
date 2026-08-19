export default function KpiCard({
  label,
  value,
  description,
  icon,
  positive,
  warning
}) {
  return (
    <div className="kpi-card">

      <div className="kpi-top">

        <span className="kpi-label">
          {label}
        </span>

        <span
          className={
            warning
              ? "kpi-icon warning"
              : positive
                ? "kpi-icon positive"
                : "kpi-icon"
          }
        >
          {icon}
        </span>

      </div>

      <div className="kpi-value">
        {value}
      </div>

      <div className="kpi-description">
        {description}
      </div>

    </div>
  );
}
