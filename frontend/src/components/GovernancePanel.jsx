export default function GovernancePanel({
  humanReview,
  governance,
  governanceReason,
  governanceRules,
  reviewing,
  reviewMessage,
  onReview
}) {
  const reviewPassed =
    governance?.gate === "PASSED" &&
    governance?.decision === "APPROVED";

  const reviewRequired =
    humanReview &&
    !reviewPassed;

  return (
    <>
      {(humanReview || reviewPassed) && (

        <div className="human-review">

          <div className="review-icon">
            {reviewPassed ? "✓" : "!"}
          </div>

          <div className="review-content">

            <strong>
              {reviewPassed
                ? "Human Review abgeschlossen"
                : "Human Review erforderlich"}
            </strong>

            <span>
              {reviewPassed
                ? "Die fachliche Prüfung wurde abgeschlossen."
                : governanceReason}
            </span>

            {governanceRules.length > 0 && (
              <span>
                Rules: {governanceRules.join(" · ")}
              </span>
            )}

          </div>

          <div className="review-actions">

            <div className="review-status">
              {governance?.gate || "ACTIVE"}
            </div>

            <div className="review-buttons">

              <button
                type="button"
                className="review-button approve"
                disabled={reviewing}
                onClick={() =>
                  onReview(
                    "APPROVED",
                    "Fachliche Prüfung abgeschlossen."
                  )
                }
              >
                {reviewing
                  ? "Speichern..."
                  : "Freigeben"}
              </button>

              <button
                type="button"
                className="review-button changes"
                disabled={reviewing}
                onClick={() =>
                  onReview(
                    "REQUEST_CHANGES",
                    "Weitere fachliche Prüfung bzw. Änderungen erforderlich."
                  )
                }
              >
                Änderungen anfordern
              </button>

              <button
                type="button"
                className="review-button reject"
                disabled={reviewing}
                onClick={() =>
                  onReview(
                    "REJECTED",
                    "Fall wurde im Rahmen der fachlichen Prüfung abgelehnt."
                  )
                }
              >
                Ablehnen
              </button>

            </div>

          </div>

        </div>

      )}

      {reviewMessage && (
        <div className="review-success">
          {reviewMessage}
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
    </>
  );
}
