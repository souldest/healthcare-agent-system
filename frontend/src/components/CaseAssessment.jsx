import {
  PipelineStep,
  PipelineLine
} from "./Pipeline";

import PriorityBadge from "./PriorityBadge";


export default function CaseAssessment({
  analysis,
  dataQuality,
  process,
  triage,
  ragFindings,
  humanReview
}) {

  return (
    <>

      {/* ORCHESTRATION */}

      <div className="section-block">

        <div className="section-header">

          <div>

            <div className="panel-kicker">
              ORCHESTRATION
            </div>

            <h3>
              Agent Pipeline
            </h3>

          </div>

          <span className="completed-label">
            COMPLETED
          </span>

        </div>


        <div className="agent-pipeline">

          <PipelineStep
            number="01"
            name="Data Quality"
            status={
              dataQuality.quality_status === "VALID"
                ? "VALID"
                : "REVIEW"
            }
          />

          <PipelineLine />

          <PipelineStep
            number="02"
            name="Process Agent"
            status="ANALYZED"
          />

          <PipelineLine />

          <PipelineStep
            number="03"
            name="Medical Agent"
            status={
              ragFindings.length > 0
                ? `COMPLETED · ${ragFindings.length} RAG`
                : "COMPLETED"
            }
          />

          <PipelineLine />

          <PipelineStep
            number="04"
            name="Triage Agent"
            status={
              triage.priority || "UNKNOWN"
            }
          />

          <PipelineLine />

          <PipelineStep
            number="05"
            name="Governance Agent"
            status={
              analysis?.governance?.decision ||
              (humanReview
                ? "HUMAN_REVIEW"
                : "CLEAR")
            }
          />

        </div>

      </div>


      {/* PROCESS + QUALITY */}

      <div className="two-column">

        <div className="info-card">

          <div className="info-card-label">
            DATA QUALITY
          </div>

          <div className="info-card-value">

            <span className="success-mark">
              ✓
            </span>

            {dataQuality.quality_status ||
              "UNKNOWN"}

          </div>

          <div className="info-card-detail">

            {dataQuality.document_count || 0}
            {" "}unterstützendes Dokument

          </div>

          {dataQuality.issues?.length > 0 && (

            <div className="quality-issues">

              {dataQuality.issues.map(
                (issue, index) => (
                  <div key={index}>
                    {issue}
                  </div>
                )
              )}

            </div>

          )}

        </div>


        <div className="info-card">

          <div className="info-card-label">
            PROCESS ANALYSIS
          </div>

          <div className="process-name">
            {process.process ||
              "Not available"}
          </div>

          <div className="process-route">

            <span>
              {process.current_step ||
                "-"}
            </span>

            <span className="route-arrow">
              →
            </span>

            <span>
              {process.next_step ||
                "-"}
            </span>

          </div>

        </div>

      </div>


      {/* TRIAGE */}

      <div className="section-block">

        <div className="section-header">

          <div>

            <div className="panel-kicker">
              RISIKOBEWERTUNG
            </div>

            <h3>
              Triage-Entscheidung
            </h3>

          </div>

          <PriorityBadge
            priority={triage.priority}
          />

        </div>


        <div className="triage-box">

          <div className="triage-reason">

            <span>
              Entscheidungsgrundlage
            </span>

            <p>
              {triage.reason ||
                "Keine Begründung verfügbar."}
            </p>

          </div>


          <div className="triage-action">

            <span>
              Empfohlene Maßnahme
            </span>

            <strong>
              {analysis.recommendation ||
                "Manual review"}
            </strong>

          </div>

        </div>

      </div>

    </>
  );
}
