export function ArchitectureStep({
  number,
  title,
  description,
  final
}) {
  return (
    <div
      className={
        final
          ? "architecture-step final"
          : "architecture-step"
      }
    >

      <div className="architecture-number">
        {number}
      </div>

      <div>

        <strong>
          {title}
        </strong>

        <span>
          {description}
        </span>

      </div>

    </div>
  );
}


export function FlowArrow() {
  return (
    <div className="flow-arrow">
      →
    </div>
  );
}
