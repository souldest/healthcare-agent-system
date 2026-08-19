import { useEffect, useState } from "react";
import { getInsurerCases, getInsurerCase } from "../api";


function statusLabel(status) {
  if (status === "APPROVED") {
    return "FREIGEGEBEN";
  }

  if (status === "PENDING") {
    return "IN PRÜFUNG";
  }

  return status || "UNBEKANNT";
}


function priorityLabel(priority) {
  if (priority === "HIGH") {
    return "HOHE PRIORITÄT";
  }

  if (priority === "NORMAL") {
    return "NORMAL";
  }

  return priority || "UNBEKANNT";
}


function InsurerPortal() {
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState(null);


  useEffect(() => {
    loadCases();
  }, []);


  async function loadCases() {
    try {
      setLoading(true);
      setError(null);

      const data = await getInsurerCases();

      setCases(data.cases || []);

      if (data.cases?.length > 0) {
        await loadCase(data.cases[0].case_id);
      }
    } catch (err) {
      setError(
        err?.message ||
        "Versicherer-Daten konnten nicht geladen werden."
      );
    } finally {
      setLoading(false);
    }
  }


  async function loadCase(caseId) {
    try {
      setDetailLoading(true);
      setError(null);

      const data = await getInsurerCase(caseId);

      setSelectedCase(data);
    } catch (err) {
      setError(
        err?.message ||
        "Falldetails konnten nicht geladen werden."
      );
    } finally {
      setDetailLoading(false);
    }
  }


  if (loading) {
    return (
      <div className="insurer-portal">
        <div className="insurer-loading">
          Versicherer-Daten werden geladen ...
        </div>
      </div>
    );
  }


  return (
    <div className="insurer-portal">

      <div className="insurer-header">

        <div>
          <div className="panel-kicker">
            INSURER PORTAL
          </div>

          <h1>
            BKK Fallportal
          </h1>

          <p>
            Freigegebene Falldaten für die weitere
            Bearbeitung durch den Versicherer.
          </p>
        </div>

        <div className="insurer-status">
          <span className="insurer-status-dot" />
          PORTAL ONLINE
        </div>

      </div>


      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}


      <div className="insurer-grid">

        <section className="insurer-cases-panel">

          <div className="insurer-section-header">

            <div>
              <div className="panel-kicker">
                CASE MANAGEMENT
              </div>

              <h2>
                Fälle
              </h2>
            </div>

            <span className="case-count">
              {cases.length}
            </span>

          </div>


          <div className="insurer-case-list">

            {cases.map((item) => {

              const active =
                selectedCase?.case_id === item.case_id;

              return (
                <button
                  key={item.case_id}
                  type="button"
                  className={
                    `insurer-case-row ${
                      active ? "active" : ""
                    }`
                  }
                  onClick={() =>
                    loadCase(item.case_id)
                  }
                >

                  <div className="insurer-case-top">

                    <strong>
                      CASE #{item.case_id}
                    </strong>

                    <span
                      className={
                        `insurer-priority ${
                          item.priority?.toLowerCase()
                        }`
                      }
                    >
                      {item.priority}
                    </span>

                  </div>


                  <div className="insurer-case-type">
                    {item.case_type}
                  </div>


                  <div className="insurer-case-description">
                    {item.description ||
                      "Keine Fallbeschreibung verfügbar."}
                  </div>


                  <div className="insurer-case-footer">

                    <span>
                      {statusLabel(item.review_status)}
                    </span>

                    <span>
                      {item.workflow_status}
                    </span>

                  </div>

                </button>
              );
            })}

          </div>

        </section>


        <section className="insurer-detail-panel">

          {detailLoading ? (

            <div className="insurer-loading">
              Falldetails werden geladen ...
            </div>

          ) : selectedCase ? (

            <>

              <div className="insurer-detail-header">

                <div>

                  <div className="panel-kicker">
                    CASE #{selectedCase.case_id}
                  </div>

                  <h2>
                    {selectedCase.case.case_type}
                  </h2>

                  <p>
                    {selectedCase.case.description}
                  </p>

                </div>

                <div
                  className={
                    `insurer-detail-priority ${
                      selectedCase.case.priority?.toLowerCase()
                    }`
                  }
                >
                  {priorityLabel(
                    selectedCase.case.priority
                  )}
                </div>

              </div>


              <div className="insurer-status-grid">

                <div className="insurer-info-card">

                  <span>
                    BEARBEITUNGSSTATUS
                  </span>

                  <strong>
                    {selectedCase.workflow.status}
                  </strong>

                </div>


                <div className="insurer-info-card">

                  <span>
                    FACHLICHE PRÜFUNG
                  </span>

                  <strong>
                    {statusLabel(
                      selectedCase.decision.review_status
                    )}
                  </strong>

                </div>


                <div className="insurer-info-card">

                  <span>
                    ENTSCHEIDUNGS-GATE
                  </span>

                  <strong>
                    {selectedCase.decision.gate}
                  </strong>

                </div>

              </div>


              <div className="insurer-section">

                <div className="panel-kicker">
                  VERSICHERTER
                </div>

                <h3>
                  {selectedCase.patient.first_name}{" "}
                  {selectedCase.patient.last_name}
                </h3>

                <div className="insurer-patient-meta">
                  Versicherungsnummer:{" "}
                  {selectedCase.patient.insurance_number}
                </div>

              </div>


              <div className="insurer-section">

                <div className="panel-kicker">
                  WORKFLOW
                </div>

                <div className="insurer-workflow">

                  <div>
                    <span>
                      Aktueller Schritt
                    </span>

                    <strong>
                      {selectedCase.workflow.current_step ||
                        "—"}
                    </strong>
                  </div>

                  <div className="insurer-arrow">
                    →
                  </div>

                  <div>
                    <span>
                      Nächster Schritt
                    </span>

                    <strong>
                      {selectedCase.workflow.next_step ||
                        "—"}
                    </strong>
                  </div>

                </div>

              </div>


              <div className="insurer-recommendation">

                <div className="panel-kicker">
                  EMPFOHLENE MASSNAHME
                </div>

                <h3>
                  {selectedCase.decision.recommended_action ||
                    "Keine Maßnahme hinterlegt."}
                </h3>

              </div>


              <div className="insurer-section">

                <div className="insurer-section-header">

                  <div>
                    <div className="panel-kicker">
                      DOKUMENTE
                    </div>

                    <h3>
                      Freigegebene Unterlagen
                    </h3>
                  </div>

                  <span className="case-count">
                    {selectedCase.documents.length}
                  </span>

                </div>


                <div className="insurer-documents">

                  {selectedCase.documents.length > 0 ? (

                    selectedCase.documents.map(
                      (document, index) => (
                        <div
                          className="insurer-document"
                          key={index}
                        >

                          <span className="document-icon">
                            DOC
                          </span>

                          <div>
                            <strong>
                              {document.filename}
                            </strong>

                            <span>
                              {document.document_type}
                            </span>
                          </div>

                          <span className="document-status">
                            FREIGEGEBEN
                          </span>

                        </div>
                      )
                    )

                  ) : (

                    <div className="muted">
                      Keine freigegebenen Dokumente.
                    </div>

                  )}

                </div>

              </div>


              <div className="insurer-notice">

                <strong>
                  Informationshinweis
                </strong>

                <span>
                  Diese Ansicht enthält ausschließlich
                  für die Versicherer-Bearbeitung
                  freigegebene Falldaten.
                </span>

              </div>

            </>

          ) : (

            <div className="insurer-empty">
              Bitte einen Fall auswählen.
            </div>

          )}

        </section>

      </div>

    </div>
  );
}


export default InsurerPortal;
