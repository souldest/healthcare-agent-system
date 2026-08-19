export function PipelineStep({
  number,
  name,
  status
}) {
  return (
    <div className="pipeline-step">

      <div className="pipeline-number">
        {number}
      </div>

      <div className="pipeline-name">
        {name}
      </div>

      <div className="pipeline-status">
        {status}
      </div>

    </div>
  );
}


export function PipelineLine() {
  return (
    <div className="pipeline-line">
      →
    </div>
  );
}
