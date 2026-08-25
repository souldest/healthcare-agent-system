export default function MedicalAnalysis({
  medicalAnalysis,
  findings,
  ragFindings,
  documents
}) {
  const displayFindings = (findings || []).map((finding) => {
    const text = String(finding);

    if (text === "Brustschmerze") {
      return "Brustschmerzen";
    }

    return text;
  });

  return (
    <>
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


        {displayFindings.length > 0 && (

          <div className="findings">

            {displayFindings.map(
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
    </>
  );
}
