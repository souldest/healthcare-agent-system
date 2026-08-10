import { useEffect, useMemo, useState } from "react";

import {
  getPatients,
  getCases,
  analyzeCase
} from "./api";


function App() {

  const [patients, setPatients] = useState([]);
  const [cases, setCases] = useState([]);

  const [selectedCase, setSelectedCase] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);

  const [error, setError] = useState(null);


  useEffect(() => {

    async function loadData() {

      try {

        setLoading(true);
        setError(null);

        const [
          patientsData,
          casesData
        ] = await Promise.all([
          getPatients(),
          getCases()
        ]);

        setPatients(patientsData || []);
        setCases(casesData || []);

      } catch (err) {

        setError(
          err.message ||
          "Daten konnten nicht geladen werden."
        );

      } finally {

        setLoading(false);
      }
    }

    loadData();

  }, []);


  async function handleAnalyze(caseItem) {

    try {

      setAnalyzing(true);
      setError(null);

      setSelectedCase(caseItem);
      setAnalysis(null);

      const result = await analyzeCase(caseItem.id);

      setAnalysis(result);

    } catch (err) {

      setError(
        err.message ||
        "Analyse konnte nicht durchgeführt werden."
      );

    } finally {

      setAnalyzing(false);
    }
  }


  function getPatient(patientId) {

    return patients.find(
      (patient) => patient.id === patientId
    );
  }


  const highPriorityCases = useMemo(
    () =>
      cases.filter(
        (item) => item.priority === "HIGH"
      ).length,
    [cases]
  );


  if (loading) {

    return (
      <div className="app-shell loading-screen">

        <div className="loading-card">

          <div className="brand-mark">
            MB
          </div>

          <div className="loading-spinner" />

          <h2>
            BKK AI Operations
          </h2>

          <p>
            Initialisiere Agentic-AI-Workflow...
          </p>

        </div>

      </div>
    );
  }


  return (

    <div className="app-shell">

      {/* =====================================================
          TOP NAVIGATION
      ===================================================== */}

      <header className="topbar">

        <div className="brand">

          <div className="brand-mark">
            MB
          </div>

          <div>

            <div className="brand-title">
              BKK AI Operations
            </div>

            <div className="brand-subtitle">
              Agentic AI · Healthcare Workflow
            </div>

          </div>

        </div>


        <div className="topbar-right">

          <div className="environment">
            DEMO ENVIRONMENT
          </div>

          <div className="system-online">

            <span className="online-dot" />

            System online

          </div>

        </div>

      </header>


      {/* =====================================================
          PAGE HEADER
      ===================================================== */}

      <main className="dashboard">

        <section className="page-heading">

          <div>

            <div className="eyebrow">
              AI ECOSYSTEM
            </div>

            <h1>
              BKK Case Intelligence
            </h1>

            <p>
              Agentic Workflow für Datenqualität,
              Prozessanalyse und Human-in-the-Loop
            </p>

          </div>


          <div className="workflow-badge">

            <span className="workflow-dot" />

            Workflow aktiv

          </div>

        </section>


        {error && (

          <div className="error-banner">

            <strong>
              Systemfehler
            </strong>

            <span>
              {error}
            </span>

          </div>

        )}


        {/* =====================================================
            KPI CARDS
        ===================================================== */}

        <section className="kpi-grid">

          <KpiCard
            label="Aktive Fälle"
            value={cases.length}
            description="Fälle im Workflow"
            icon="◈"
          />

          <KpiCard
            label="Data Quality"
            value="100%"
            description="Demo-Datensatz valide"
            icon="✓"
            positive
          />

          <KpiCard
            label="Hohe Priorität"
            value={highPriorityCases}
            description="Fälle mit Handlungsbedarf"
            icon="!"
            warning={highPriorityCases > 0}
          />

          <KpiCard
            label="Agent Pipeline"
            value="5"
            description="Specialized Agents"
            icon="◎"
          />

        </section>


        {/* =====================================================
            MAIN GRID
        ===================================================== */}

        <section className="main-grid">


          {/* ===================================================
              CASE LIST
          =================================================== */}

          <div className="panel cases-panel">

            <div className="panel-header">

              <div>

                <div className="panel-kicker">
                  CASE MANAGEMENT
                </div>

                <h2>
                  Healthcare Cases
                </h2>

              </div>

              <div className="case-count">
                {cases.length} Cases
              </div>

            </div>


            <div className="case-list">

              {cases.map((caseItem) => {

                const patient =
                  getPatient(caseItem.patient_id);

                const selected =
                  selectedCase?.id === caseItem.id;

                const isAnalyzing =
                  analyzing &&
                  selectedCase?.id === caseItem.id;


                return (

                  <button
                    className={
                      selected
                        ? "case-row selected"
                        : "case-row"
                    }
                    key={caseItem.id}
                    onClick={() =>
                      handleAnalyze(caseItem)
                    }
                    disabled={analyzing}
                  >

                    <div className="case-row-top">

                      <span className="case-id">
                        CASE #{caseItem.id}
                      </span>

                      <PriorityBadge
                        priority={
                          caseItem.priority
                        }
                      />

                    </div>


                    <div className="case-title">

                      {caseItem.case_type}

                    </div>


                    <div className="case-description">

                      {caseItem.description ||
                        "Keine Beschreibung vorhanden."}

                    </div>


                    <div className="case-footer">

                      <span>

                        {patient
                          ? `${patient.first_name} ${patient.last_name}`
                          : "Patient"}

                      </span>


                      <span>

                        {isAnalyzing
                          ? "Analysiere..."
                          : selected
                            ? "Aktiv"
                            : "Analyse starten →"}

                      </span>

                    </div>

                  </button>

                );

              })}

            </div>

          </div>


          {/* ===================================================
              ANALYSIS AREA
          =================================================== */}

          <div className="analysis-panel">

            {!analysis ? (

              <EmptyAnalysis />

            ) : (

              <AnalysisResult
                analysis={analysis}
                selectedCase={selectedCase}
                patient={
                  selectedCase
                    ? getPatient(
                        selectedCase.patient_id
                      )
                    : null
                }
              />

            )}

          </div>

        </section>


        {/* =====================================================
            ARCHITECTURE FOOTER
        ===================================================== */}

        <section className="architecture-panel">

          <div className="panel-kicker">
            AGENTIC AI ARCHITECTURE
          </div>

          <h2>
            Kontrollierter autonomer Workflow
          </h2>

          <div className="architecture-flow">

            <ArchitectureStep
              number="01"
              title="Data Quality"
              description="Validierung"
            />

            <FlowArrow />

            <ArchitectureStep
              number="02"
              title="Process Agent"
              description="Workflow analysieren"
            />

            <FlowArrow />

            <ArchitectureStep
              number="03"
              title="Medical Agent"
              description="LLM + RAG"
            />

            <FlowArrow />

            <ArchitectureStep
              number="04"
              title="Triage Agent"
              description="Risiko bewerten"
            />

            <FlowArrow />

            <ArchitectureStep
              number="05"
              title="Governance Agent"
              description="Entscheidungs-Gate"
            />

            <FlowArrow />

            <ArchitectureStep
              number="06"
              title="Human Review"
              description="Kontrollierte Übergabe"
              final
            />

          </div>

        </section>


        <footer className="dashboard-footer">

          <span>
            BKK AI Operations · Prototype
          </span>

          <span>
            Human-in-the-Loop · Data Governance · RAG
          </span>

        </footer>

      </main>

    </div>
  );
}


/* =============================================================
   KPI CARD
============================================================= */

function KpiCard({
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


/* =============================================================
   PRIORITY
============================================================= */

function PriorityBadge({ priority }) {

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


/* =============================================================
   EMPTY STATE
============================================================= */

function EmptyAnalysis() {

  return (

    <div className="empty-analysis">

      <div className="empty-symbol">
        AI
      </div>

      <div className="panel-kicker">
        CASE INTELLIGENCE
      </div>

      <h2>
        Select a case
      </h2>

      <p>
        Wähle einen Fall aus der linken Liste,
        um den vollständigen Agentic-AI-Workflow
        auszuführen.
      </p>


      <div className="empty-features">

        <span>✓ Data Quality</span>
        <span>✓ Process Analysis</span>
        <span>✓ Medical AI</span>
        <span>✓ RAG</span>
        <span>✓ Human Review</span>

      </div>

    </div>
  );
}


/* =============================================================
   ANALYSIS RESULT
============================================================= */

function AnalysisResult({
  analysis,
  selectedCase,
  patient
}) {

  const medical =
    analysis?.medical_analysis || {};

  const medicalAnalysis =
    medical?.analysis || {};

  const triage =
    analysis?.triage || {};

  const dataQuality =
    analysis?.data_quality || {};

  const process =
    analysis?.process_analysis || {};

  const governance =
    analysis?.governance || {};


  const risk =
    medical?.risk_level ||
    medicalAnalysis?.risk_level ||
    "UNKNOWN";


  const findings =
    medicalAnalysis?.findings || [];


  const documents =
    medical?.documents || [];


  const ragFindings =
    medical?.rag_findings || [];


  const humanReview =
    analysis?.human_review_required === true ||
    governance?.human_review_required === true;

  const governanceRules =
    governance?.rules_triggered || [];

  const governanceReason =
    governance?.reason ||
    "Eine qualifizierte fachliche Prüfung durch Mitarbeitende ist vor der weiteren Bearbeitung erforderlich.";


  return (

    <div className="analysis-content">


      {/* HEADER */}

      <div className="analysis-header">

        <div>

          <div className="panel-kicker">
            CASE #{analysis.case_id}
          </div>

          <h2>
            {selectedCase?.case_type ||
              "Case Analysis"}
          </h2>

          <div className="analysis-patient">

            {patient
              ? `${patient.first_name} ${patient.last_name}`
              : "Patient"}

            <span>·</span>

            {analysis.workflow}

          </div>

        </div>


        <div className="risk-block">

          <span className="risk-label">
            RISK LEVEL
          </span>

          <span
            className={`risk-value ${risk.toLowerCase()}`}
          >
            {risk}
          </span>

        </div>

      </div>


      {/* HUMAN REVIEW */}

      {humanReview && (

        <div className="human-review">

          <div className="review-icon">
            !
          </div>

          <div className="review-content">

            <strong>
              Human Review erforderlich
            </strong>

            <span>
              {governanceReason}
            </span>

            {governanceRules.length > 0 && (
              <span>
                Rules: {governanceRules.join(" · ")}
              </span>
            )}

          </div>

          <div className="review-status">
            {governance?.gate || "ACTIVE"}
          </div>

        </div>

      )}


      {governance?.decision && (

        <div className="section-block governance-block">

          <div className="section-header">

            <div>

              <div className="panel-kicker">
                GOVERNANCE
              </div>

              <h3>
                Entscheidungs-Gate
              </h3>

            </div>

            <span className="ai-label">
              {governance.decision}
            </span>

          </div>

          <div className="triage-box">

            <div className="triage-reason">
              <span>
                Entscheidungsgrundlage
              </span>
              <p>
                {governanceReason}
              </p>
            </div>

            <div className="triage-action">
              <span>
                Review-Gate
              </span>
              <strong>
                {governance.gate || "ACTIVE"}
              </strong>
            </div>

          </div>

        </div>
      )}


      {/* AGENT STATUS */}

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


      {/* MEDICAL ANALYSIS */}

      <div className="section-block">

        <div className="section-header">

          <div>

            <div className="panel-kicker">
              AI ANALYSIS
            </div>

            <h3>
              Medizinische Befunde
            </h3>

          </div>

          <span className="ai-label">
            LLM + RAG
          </span>

        </div>


        <div className="summary-box">

          {medicalAnalysis.summary ||
            "Keine Zusammenfassung verfügbar."}

        </div>


        {findings.length > 0 && (

          <div className="findings">

            {findings.map(
              (finding, index) => (

                <div
                  className="finding"
                  key={index}
                >

                  <span>
                    {String(index + 1).padStart(
                      2,
                      "0"
                    )}
                  </span>

                  <p>
                    {finding}
                  </p>

                </div>

              )
            )}

          </div>

        )}

      </div>


      {/* RAG */}

      <div className="section-block">

        <div className="section-header">

          <div>

            <div className="panel-kicker">
              KNOWLEDGE RETRIEVAL
            </div>

            <h3>
              RAG-Nachweise
            </h3>

          </div>

          <span className="ai-label">
            {ragFindings.length} Dokument abgerufen
          </span>

        </div>


        {ragFindings.length > 0 ? (

          <div className="rag-list">

            {ragFindings.map(
              (item, index) => (

                <div
                  className="rag-card"
                  key={index}
                >

                  <div className="rag-top">

                    <span>
                      SOURCE {String(index + 1).padStart(
                        2,
                        "0"
                      )}
                    </span>

                    <span>
                      {item.filename ||
                        "Medical document"}
                    </span>

                  </div>


                  <p>
                    {item.content}
                  </p>


                  {item.distance !== undefined && (

                    <div className="similarity">

                      Retrieval distance:{" "}
                      {Number(
                        item.distance
                      ).toFixed(4)}

                    </div>

                  )}

                </div>

              )
            )}

          </div>

        ) : (

          <div className="muted">
            Keine RAG-Ergebnisse vorhanden.
          </div>

        )}

      </div>


      {/* DOCUMENTS */}

      <div className="section-block">

        <div className="section-header">

          <div>

            <div className="panel-kicker">
              DATENQUELLEN
            </div>

            <h3>
              Documents
            </h3>

          </div>

          <span className="document-count">
            {documents.length}
          </span>

        </div>


        <div className="documents">

          {documents.length > 0 ? (

            documents.map(
              (document, index) => (

                <div
                  className="document-row"
                  key={index}
                >

                  <span className="document-icon">
                    DOC
                  </span>

                  <div>

                    <strong>
                      {document.filename ||
                        "Document"}
                    </strong>

                    <span>
                      {document.document_type ||
                        "medical_report"}
                    </span>

                  </div>

                  <span className="document-status">
                    INDEXIERT
                  </span>

                </div>

              )
            )

          ) : (

            <div className="muted">
              Keine Dokumente vorhanden.
            </div>

          )}

        </div>

      </div>


      {/* RECOMMENDATION */}

      <div className="recommendation-box">

        <div className="recommendation-kicker">
          EMPFOHLENE MAßNAHME
        </div>

        <h3>
          {medicalAnalysis.recommended_action ||
            "Manual review required"}
        </h3>

        <p>
          KI-Unterstützung mit kontrollierter
          Übergabe an qualifizierte Mitarbeitende.
        </p>

      </div>


      <div className="disclaimer">

        <strong>
          Governance Notice
        </strong>

        <span>
          Diese Anwendung ist ein technischer
          Demonstrator. KI-Ergebnisse sind
          Entscheidungshilfen und ersetzen keine
          fachliche oder medizinische Entscheidung.
        </span>

      </div>

    </div>
  );
}


/* =============================================================
   PIPELINE COMPONENTS
============================================================= */

function PipelineStep({
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


function PipelineLine() {

  return (
    <div className="pipeline-line">
      →
    </div>
  );
}


/* =============================================================
   ARCHITECTURE
============================================================= */

function ArchitectureStep({
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


function FlowArrow() {

  return (
    <div className="flow-arrow">
      →
    </div>
  );
}


export default App;
