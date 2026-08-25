import { useEffect, useMemo, useState } from "react";

import {
  getPatients,
  getCases,
  analyzeCase,
  getCaseHistory,
  submitHumanReview,
  getCaseAnalytics,
  getSickPayAnalytics,
  getCaseSummary
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

  const [caseAnalytics, setCaseAnalytics] = useState([]);
  const [sickPayAnalytics, setSickPayAnalytics] = useState([]);
  const [caseSummary, setCaseSummary] = useState(null);

  const [selectedCase, setSelectedCase] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [history, setHistory] = useState([]);

  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [reviewing, setReviewing] = useState(false);
  const [reviewMessage, setReviewMessage] = useState(null);

  const [error, setError] = useState(null);

  const [view, setView] = useState("operations");

  const getPatient = (patientId) =>
    patients.find(
      (patient) => patient.id === patientId
    );

  const highPriorityCases = cases.filter(
    (caseItem) =>
      caseItem.priority === "HIGH" ||
      caseItem.priority === "high" ||
      caseItem.priority === "CRITICAL" ||
      caseItem.priority === "critical"
  ).length;



  useEffect(() => {

    async function loadData() {

      try {

        setLoading(true);
        setError(null);

        const results = await Promise.allSettled([
          getPatients(),
          getCases(),
          getCaseAnalytics(),
          getSickPayAnalytics(),
          getCaseSummary()
        ]);

        console.log("API RESULTS:", results);

        const [
          patientsResult,
          casesResult,
          caseAnalyticsResult,
          sickPayAnalyticsResult,
          caseSummaryResult
        ] = results;

        if (patientsResult.status === "rejected") {
          throw new Error(
            `getPatients(): ${patientsResult.reason?.message || patientsResult.reason}`
          );
        }

        if (casesResult.status === "rejected") {
          throw new Error(
            `getCases(): ${casesResult.reason?.message || casesResult.reason}`
          );
        }

        if (caseAnalyticsResult.status === "rejected") {
          throw new Error(
            `getCaseAnalytics(): ${caseAnalyticsResult.reason?.message || caseAnalyticsResult.reason}`
          );
        }

        if (sickPayAnalyticsResult.status === "rejected") {
          throw new Error(
            `getSickPayAnalytics(): ${sickPayAnalyticsResult.reason?.message || sickPayAnalyticsResult.reason}`
          );
        }

        if (caseSummaryResult.status === "rejected") {
          throw new Error(
            `getCaseSummary(): ${caseSummaryResult.reason?.message || caseSummaryResult.reason}`
          );
        }

        const patientsData = patientsResult.value;
        const casesData = casesResult.value;
        const caseAnalyticsData = caseAnalyticsResult.value;
        const sickPayAnalyticsData = sickPayAnalyticsResult.value;
        const caseSummaryData = caseSummaryResult.value;

        setPatients(patientsData || []);
        setCases(casesData || []);
        setCaseAnalytics(caseAnalyticsData || []);
        setSickPayAnalytics(sickPayAnalyticsData || []);
        setCaseSummary(caseSummaryData || null);

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

      const reviewResult =
        await submitHumanReview(
          selectedCase.id,
          decision,
          "Human Reviewer",
          comment
        );

      /*
       * Das vom Backend rekonstruierte Ergebnis direkt übernehmen.
       *
       * WICHTIG:
       * Nach Human Review KEIN analyzeCase() ausführen.
       * Ein neuer Analyse-Run würde das Governance-Gate erneut
       * erzeugen und die gerade getroffene Fachentscheidung
       * überschreiben.
       */
      if (reviewResult?.analysis) {
        setAnalysis(reviewResult.analysis);
      }

      // Nach der Human-Review-Entscheidung NICHT erneut
      // analyzeCase() aufrufen.
      //
      // Ein erneuter analyzeCase()-Aufruf würde einen neuen
      // Workflow-Run starten und unmittelbar wieder ein
      // HUMAN_REVIEW-Gate erzeugen.
      //
      // Deshalb nur den aktuellen Audit Trail neu laden.

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
            value={caseSummary?.open_cases ?? cases.length}
            description="Offene Fälle laut Databricks"
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
            value={caseSummary?.high_priority_cases ?? highPriorityCases}
            description="Fälle mit Handlungsbedarf"
            icon="!"
            warning={(caseSummary?.high_priority_cases ?? highPriorityCases) > 0}
          />

          <KpiCard
              label="Kategorien"
              value={caseSummary?.total_categories ?? caseAnalytics.length}
              description="Case-Kategorien in Databricks"
            icon="◎"
          />

        </section>


        {/* =====================================================
            DATABRICKS ANALYTICS
        ===================================================== */}

        <section className="analytics-panel">

          <div className="panel-header">

            <div>
              <div className="panel-kicker">
                DATABRICKS ANALYTICS
              </div>

              <h2>
                Healthcare Case Analytics
              </h2>
            </div>

            <div className="case-count">
              {caseAnalytics.length} Kategorien
            </div>

          </div>


          <div className="analytics-grid">

            {caseAnalytics.map((item) => (

              <div
                className="analytics-card"
                key={item.case_type}
              >

                <div className="analytics-card-header">
                  <strong>
                    {item.case_type}
                  </strong>

                  <span>
                    {item.total_cases} Fälle
                  </span>
                </div>

                <div className="analytics-metrics">

                  <div>
                    <span>Offen</span>
                    <strong>
                      {item.open_cases}
                    </strong>
                  </div>

                  <div>
                    <span>High Priority</span>
                    <strong>
                      {item.high_priority_cases}
                    </strong>
                  </div>

                  <div>
                    <span>Geschlossen</span>
                    <strong>
                      {item.closed_cases}
                    </strong>
                  </div>

                </div>

              </div>

            ))}


            {sickPayAnalytics.map((item) => (

              <div
                className="analytics-card sick-pay-card"
                key={`sick-pay-${item.case_type}`}
              >

                <div className="analytics-card-header">
                  <strong>
                    Sick Pay
                  </strong>

                  <span>
                    {item.total_cases} Fälle
                  </span>
                </div>

                <div className="analytics-metrics">

                  <div>
                    <span>Offen</span>
                    <strong>
                      {item.open_cases}
                    </strong>
                  </div>

                  <div>
                    <span>High Priority</span>
                    <strong>
                      {item.high_priority_cases}
                    </strong>
                  </div>

                </div>

              </div>

            ))}

          </div>

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

  console.log("=== ANALYSIS RESULT DEBUG ===");
  console.log("analysis:", analysis);
  console.log("medical_analysis:", analysis?.medical_analysis);
  console.log("triage:", analysis?.triage);
  console.log("governance:", analysis?.governance);

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


  /*
   * ============================================================
   * HUMAN REVIEW / GOVERNANCE
   * ============================================================
   *
   * Eine finale Freigabe liegt ausschließlich dann vor, wenn
   * Governance explizit APPROVED + PASSED meldet und kein
   * Human Review mehr erforderlich ist.
   *
   * HIGH / CRITICAL erzwingen eine fachliche Prüfung.
   * Dadurch kann ein Risiko-Case nicht versehentlich als CLEAR
   * dargestellt werden, nur weil ein älterer Governance-Run
   * noch APPROVED enthält.
   */

  const riskUpper =
    String(risk || "UNKNOWN").toUpperCase();

  const triagePriority =
    String(triage?.priority || "").toUpperCase();

  const isHighRisk =
    riskUpper === "HIGH" ||
    riskUpper === "CRITICAL" ||
    triagePriority === "HIGH" ||
    triagePriority === "CRITICAL";

  const explicitHumanReviewRequired =
    analysis?.human_review_required === true ||
    governance?.human_review_required === true;

  /*
   * WICHTIG:
   *
   * governance.decision === "APPROVED" ist KEINE Human-Review-
   * Entscheidung.
   *
   * Eine Freigabe darf erst dann als abgeschlossen dargestellt
   * werden, wenn tatsächlich eine Human-Review-Entscheidung
   * dokumentiert wurde.
   */
  const rawHumanReviewDecision =
    governance?.human_review_decision ??
    governance?.human_review?.decision ??
    null;

  const normalizedHumanDecision =
    String(rawHumanReviewDecision || "").toUpperCase();

  const humanReviewApproved =
    normalizedHumanDecision === "APPROVED";

  const humanReviewRejected =
    normalizedHumanDecision === "REJECTED";

  const humanReviewChangesRequested =
    normalizedHumanDecision === "REQUEST_CHANGES" ||
    normalizedHumanDecision === "CHANGES REQUESTED";

  /*
   * HIGH/CRITICAL oder explizites Review-Gate:
   * solange keine echte Human-Review-Entscheidung vorliegt,
   * bleibt der Fall im HUMAN_REVIEW-Zustand.
   */
  const humanReviewRequired =
    !humanReviewApproved &&
    !humanReviewRejected &&
    !humanReviewChangesRequested &&
    (
      explicitHumanReviewRequired ||
      isHighRisk
    );

  /*
   * Ein Fall ist nur dann wirklich abgeschlossen,
   * wenn die Human Review tatsächlich APPROVED wurde.
   *
   * Bei nicht-reviewpflichtigen Fällen darf Governance selbst
   * APPROVED/PASSED sein.
   */
  const governanceApprovedWithoutHumanReview =
    !isHighRisk &&
    !explicitHumanReviewRequired &&
    governance?.decision === "APPROVED" &&
    governance?.gate === "PASSED" &&
    governance?.human_review_required === false;

  const reviewApproved =
    humanReviewApproved ||
    governanceApprovedWithoutHumanReview;

  const humanReview =
    humanReviewRequired;

  const governanceRules =
    governance?.rules_triggered || [];

  const governanceReason =
    governance?.reason ||
    (
      isHighRisk
        ? "Aufgrund des erhöhten medizinischen Risikos ist eine qualifizierte fachliche Prüfung durch Mitarbeitende erforderlich."
        : "Eine qualifizierte fachliche Prüfung durch Mitarbeitende ist vor der weiteren Bearbeitung erforderlich."
    );

  const decision =
    String(governance?.decision || "").toUpperCase();

  const gate =
    String(governance?.gate || "").toUpperCase();

  const controlledContinue =
    decision === "CONTROLLED_CONTINUE" &&
    gate === "PASS" &&
    !humanReviewRequired;

  const currentGovernanceStatus =
    humanReviewApproved
      ? "APPROVED"
      : humanReviewRejected
        ? "REJECTED"
        : humanReviewChangesRequested
          ? "REQUEST_CHANGES"
          : controlledContinue
            ? "CONTROLLED_CONTINUE"
            : humanReviewRequired
              ? "HUMAN_REVIEW"
              : governanceApprovedWithoutHumanReview
                ? "APPROVED"
                : decision || "PENDING";

  const currentGovernanceGate =
    humanReviewApproved ||
    governanceApprovedWithoutHumanReview
      ? "PASSED"
      : controlledContinue
        ? "PASS"
        : humanReviewRequired
          ? "HUMAN_REVIEW"
          : gate || "ACTIVE";

  const currentHumanReviewStatus =
    humanReviewApproved
      ? "COMPLETED"
      : humanReviewRejected
        ? "REJECTED"
        : humanReviewChangesRequested
          ? "REQUEST_CHANGES"
          : humanReviewRequired
            ? "REQUIRED"
            : controlledContinue
              ? "NOT_REQUIRED"
              : "NOT_REQUIRED";

  const currentHumanReviewDecision =
    humanReviewApproved ||
    humanReviewRejected ||
    humanReviewChangesRequested
      ? normalizedHumanDecision
      : null;


  const auditHistory = Array.isArray(history)
    ? history.map((event, index, events) => {

        const isLatestGovernanceEvent =
          event?.agent === "Governance Agent" &&
          event?.action === "GOVERNANCE_DECISION" &&
          index === events
            .map((item, i) =>
              item?.agent === "Governance Agent" &&
              item?.action === "GOVERNANCE_DECISION"
                ? i
                : -1
            )
            .filter(i => i >= 0)
            .pop();

        if (!isLatestGovernanceEvent) {
          return event;
        }

        /*
         * Der letzte Governance-Eintrag ist historisch.
         * Für die Anzeige des aktuellen Status wird er mit dem
         * aktuellen Governance-/Human-Review-Ergebnis gespiegelt.
         */
        return {
          ...event,
          status: currentGovernanceStatus,
          result: JSON.stringify({
            agent: "governance_agent",
            case_id: analysis.case_id,
            decision: currentGovernanceStatus,
            gate: currentGovernanceGate,
            human_review_required: humanReview,
            reason: governanceReason,
            rules_triggered: governanceRules,
            risk_level: risk,
            triage_priority: triage?.priority || risk,
            data_quality_status:
              dataQuality?.quality_status || "VALID",
            human_review_status: currentHumanReviewStatus,
            human_review_decision:
              currentHumanReviewDecision
          }),
          current: true
        };
      })
    : [];


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


      <section className="agent-pipeline-panel">

        <div className="panel-kicker">
          AGENT PIPELINE
        </div>

        <h3>
          Spezialisierte Agenten
        </h3>

        <div className="agent-pipeline-grid">

          <div className="agent-card">
            <span className="agent-number">01</span>
            <div>
              <strong>Data Quality Agent</strong>
              <span>Datenqualität und Dokumente validieren</span>
            </div>
            <b>VALID</b>
          </div>

          <div className="agent-card">
            <span className="agent-number">02</span>
            <div>
              <strong>Process Agent</strong>
              <span>Workflow und nächsten Prozessschritt analysieren</span>
            </div>
            <b>ANALYZED</b>
          </div>

          <div className="agent-card">
            <span className="agent-number">03</span>
            <div>
              <strong>Medical Agent</strong>
              <span>Medizinische Analyse mit LLM + RAG</span>
            </div>
            <b>COMPLETED</b>
          </div>

          <div className="agent-card">
            <span className="agent-number">04</span>
            <div>
              <strong>Triage Agent</strong>
              <span>Risiko und Priorität bewerten</span>
            </div>
            <b>{risk}</b>
          </div>

          <div className="agent-card">
            <span className="agent-number">05</span>
            <div>
              <strong>Governance Agent</strong>
              <span>Entscheidungs-Gate und Regeln prüfen</span>
            </div>
            <b>
              {currentGovernanceStatus}
            </b>
          </div>

          <div className="agent-card human-agent">
            <span className="agent-number">06</span>
            <div>
              <strong>Human Review</strong>
              <span>Kontrollierte fachliche Übergabe</span>
            </div>
            <b>
              {currentHumanReviewStatus}
            </b>
          </div>

        </div>

      </section>


      <MedicalAnalysis
        medicalAnalysis={medicalAnalysis}
        findings={findings}
        ragFindings={ragFindings}
        documents={documents}
      />


      <CaseAssessment
        analysis={analysis}
        dataQuality={dataQuality}
        process={process}
        triage={triage}
        ragFindings={ragFindings}
        humanReview={humanReview}
      />


      <GovernancePanel
        humanReview={humanReview}
        governance={governance}
        governanceReason={governanceReason}
        governanceRules={governanceRules}
        reviewing={reviewing}
        reviewMessage={reviewMessage}
        onReview={handleHumanReview}
      />


      <AuditTrail
        history={auditHistory}
        governance={governance}
        humanReview={humanReview}
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
