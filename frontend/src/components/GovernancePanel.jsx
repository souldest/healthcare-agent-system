export default function GovernancePanel({
  humanReview,
  governance,
  governanceReason,
  governanceRules = [],
  reviewing,
  reviewMessage,
  onReview
}) {
  const decision =
    String(governance?.decision || "").toUpperCase();

  const gate =
    String(governance?.gate || "").toUpperCase();

  const reviewPassed =
    gate === "PASSED" &&
    decision === "APPROVED";

  const controlledContinue =
    decision === "CONTROLLED_CONTINUE";

  const reviewRequired =
    humanReview && !reviewPassed;

  const latestReview =
    governance?.human_review || null;

  const humanDecision =
    latestReview?.status ||
    latestReview?.decision ||
    null;

  const reviewer =
    latestReview?.agent ||
    latestReview?.reviewer ||
    null;

  const normalizedHumanDecision =
    String(humanDecision || "").toUpperCase();

  const hasHumanDecision =
    normalizedHumanDecision === "APPROVED" ||
    normalizedHumanDecision === "REJECTED" ||
    normalizedHumanDecision === "REQUEST_CHANGES" ||
    normalizedHumanDecision === "CHANGES_REQUESTED";

  const humanReviewStatus =
    reviewPassed || hasHumanDecision
      ? "COMPLETED"
      : reviewRequired
        ? "REQUIRED"
        : "NOT_REQUIRED";

  /*
   * ------------------------------------------------------------
   * HUMAN REVIEW
   * ------------------------------------------------------------
   *
   * Nur anzeigen, wenn tatsächlich eine fachliche Prüfung
   * erforderlich ist oder bereits abgeschlossen wurde.
   *
   * CONTROLLED_CONTINUE + humanReview=false bedeutet:
   * Keine Human Review erforderlich.
   */
  {(humanReview || reviewPassed || hasHumanDecision) && (
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

        {reviewPassed && humanDecision && (
          <span>
            Entscheidung: {humanDecision}
            {reviewer ? ` · Reviewer: ${reviewer}` : ""}
          </span>
        )}

      </div>

      <div className="review-actions">

        <div className="review-status">
          {reviewPassed
            ? "PASSED"
            : reviewRequired
              ? "HUMAN_REVIEW"
              : "ACTIVE"}
        </div>

        {!reviewPassed && reviewRequired && (
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
        )}

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
            {reviewPassed
              ? "PASSED"
              : controlledContinue
                ? "PASS"
                : gate || "ACTIVE"}
          </strong>

        </div>

      </div>

      {controlledContinue && !reviewRequired && (
        <div className="review-decision-summary">

          <div className="review-decision-label">
            Human Review
          </div>

          <div className="review-decision-value">
            <strong>
              NOT_REQUIRED
            </strong>

            <span>
              Keine fachliche Prüfung erforderlich
            </span>
          </div>

        </div>
      )}

      {reviewRequired && !reviewPassed && (
        <div className="review-decision-summary">

          <div className="review-decision-label">
            Human Review
          </div>

          <div className="review-decision-value">
            <strong>
              REQUIRED
            </strong>

            <span>
              Fachliche Prüfung erforderlich
            </span>
          </div>

        </div>
      )}

      {reviewPassed && (
        <div className="review-decision-summary">

          <div className="review-decision-label">
            Fachliche Entscheidung
          </div>

          <div className="review-decision-value">

            <strong>
              APPROVED
            </strong>

            {reviewer && (
              <span>
                {reviewer}
              </span>
            )}

          </div>

        </div>
      )}

    </div>
  )}
}
