import { useEffect, useMemo, useState } from "react";

import {
  getPatients,
  getCases,
  analyzeCase,
  getCaseHistory,
  submitHumanReview
} from "./api";

import KpiCard from "./components/KpiCard";
import PriorityBadge from "./components/PriorityBadge";
import EmptyAnalysis from "./components/EmptyAnalysis";
import AuditTrail from "./components/AuditTrail";
import GovernancePanel from "./components/GovernancePanel";
import MedicalAnalysis from "./components/MedicalAnalysis";
import CaseAssessment from "./components/CaseAssessment";
import MemberPortal from "./components/MemberPortal";
import {
  ArchitectureStep,
  FlowArrow
} from "./components/Architecture";


function App() {

  const [patients, setPatients] = useState([]);
  const [cases, setCases] = useState([]);

  const [selectedCase, setSelectedCase] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [history, setHistory] = useState([]);

  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [reviewing, setReviewing] = useState(false);
  const [reviewMessage, setReviewMessage] = useState(null);

  const [error, setError] = useState(null);

  const [view, setView] = useState("operations");


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

      // ---------------------------------------------------------
      // Derselbe Fall ist bereits geöffnet:
      // keine neue Agent-Pipeline starten.
      // Nur den aktuellen Audit Trail laden.
      // ---------------------------------------------------------

      if (selectedCase?.id === caseItem.id && analysis) {

        const historyResult =
          await getCaseHistory(caseItem.id);

        setHistory(
          historyResult?.history || []
        );

        return;
      }

      // ---------------------------------------------------------
      // Neuen Fall auswählen.
      // ---------------------------------------------------------

      setSelectedCase(caseItem);
      setAnalysis(null);
      setHistory([]);

      // ---------------------------------------------------------
      // Einmalige Analyse.
      // ---------------------------------------------------------

      const result =
        await analyzeCase(caseItem.id);

      setAnalysis(result);

      // ---------------------------------------------------------
      // Audit Trail nach der Analyse laden.
      // ---------------------------------------------------------

      const historyResult =
        await getCaseHistory(caseItem.id);

      setHistory(
        historyResult?.history || []
      );

    } catch (err) {

      setError(
        err.message ||
        "Analyse konnte nicht durchgeführt werden."
      );

    } finally {

      setAnalyzing(false);
    }
  }



  async function handleHumanReview(
    decision,
    comment = null
  ) {

    if (!selectedCase?.id) {
      return;
    }

    try {

      setReviewing(true);
      setReviewMessage(null);
      setError(null);

      await submitHumanReview(
        selectedCase.id,
        decision,
        "Demo Reviewer",
        comment
      );

      // Analyse nach Human Review neu laden,
      // damit Governance, Status und Recommendation
      // sofort den aktuellen Backend-Zustand zeigen.
      const result =
        await analyzeCase(selectedCase.id);

      setAnalysis(result);

      // Audit Trail aktualisieren, ohne eine
      // zusätzliche Pipeline-Ausführung zu erzeugen.
      const historyResult =
        await getCaseHistory(
          selectedCase.id
        );

      setHistory(
        historyResult?.history || []
      );

      setReviewMessage(
        decision === "APPROVED"
          ? "Fall wurde freigegeben."
          : decision === "REJECTED"
            ? "Fall wurde abgelehnt."
            : "Änderungen wurden angefordert."
      );

    } catch (err) {

      setError(
        err.message ||
        "Human Review konnte nicht gespeichert werden."
      );

    } finally {

      setReviewing(false);

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

        <div className="view-switcher">

          <button
            type="button"
            className={
              view === "operations"
                ? "view-switcher-button active"
                : "view-switcher-button"
            }
            onClick={() => setView("operations")}
          >
            BKK AI Operations
          </button>

          <button
            type="button"
            className={
              view === "insurer"
                ? "view-switcher-button active"
                : "view-switcher-button"
            }
            onClick={() => setView("insurer")}
          >
            Versicherer-Portal
          </button>

        </div>

        {view === "insurer" ? (

          <MemberPortal />

        ) : (

          <>

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
                history={history}
                reviewing={reviewing}
                reviewMessage={reviewMessage}
                handleHumanReview={handleHumanReview}
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

          </>

        )}

      </main>

    </div>
  );
}


/* =============================================================
   ANALYSIS RESULT
============================================================= */

function AnalysisResult({
  analysis,
  selectedCase,
  patient,
  history,
  reviewing,
  reviewMessage,
  handleHumanReview
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


  const reviewApproved =
    governance?.decision === "APPROVED" &&
    governance?.gate === "PASSED" &&
    governance?.human_review_required === false;

  const humanReview =
    !reviewApproved &&
    (
      analysis?.human_review_required === true ||
      governance?.human_review_required === true
    );

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


      <GovernancePanel
        humanReview={humanReview}
        governance={governance}
        governanceReason={governanceReason}
        governanceRules={governanceRules}
        reviewing={reviewing}
        reviewMessage={reviewMessage}
        onReview={handleHumanReview}
      />


      <AuditTrail history={history} />


      <CaseAssessment
        analysis={analysis}
        dataQuality={dataQuality}
        process={process}
        triage={triage}
        ragFindings={ragFindings}
        humanReview={humanReview}
      />


      <MedicalAnalysis
        medicalAnalysis={medicalAnalysis}
        findings={findings}
        ragFindings={ragFindings}
        documents={documents}
      />


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


export default App;
