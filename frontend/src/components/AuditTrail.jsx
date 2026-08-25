function AuditTrail({
  history = [],
  governance = {},
  analysis = {}
}) {
  const workflowActions = [
    "VALIDATE_CASE",
    "ANALYZE_WORKFLOW",
    "MEDICAL_ANALYSIS",
    "RISK_ASSESSMENT",
    "GOVERNANCE_DECISION",
  ];

  const events = [...history]
    .filter(Boolean)
    .sort(
      (a, b) =>
        new Date(a.timestamp || 0).getTime() -
        new Date(b.timestamp || 0).getTime()
    );

  /*
   * Der letzte VALIDATE_CASE-Eintrag markiert
   * den Beginn des aktuellsten Workflow-Runs.
   */
  const lastValidateIndex = [...events]
    .map((event, index) => ({ event, index }))
    .reverse()
    .find(
      ({ event }) =>
        event.action === "VALIDATE_CASE"
    )?.index;

  const currentRunStart =
    lastValidateIndex !== undefined
      ? lastValidateIndex
      : 0;

  const currentRun = events.slice(currentRunStart);

  /*
   * Pro Workflow-Action nur das letzte Event
   * des aktuellen Runs anzeigen.
   */
  const latestEventByAction = (runEvents) => {
    const latest = new Map();

    runEvents.forEach((event) => {
      if (workflowActions.includes(event.action)) {
        latest.set(event.action, event);
      }
    });

    return workflowActions
      .map((action) => latest.get(action))
      .filter(Boolean);
  };

  const workflowEvents =
    latestEventByAction(currentRun);

  /*
   * Aktuellen Governance-Zustand aus /agents/analyze/{caseId}
   * als führende Quelle verwenden.
   */
  const decision =
    String(governance?.decision || "").toUpperCase();

  const gate =
    String(governance?.gate || "").toUpperCase();

  const humanReviewRequired =
    governance?.human_review_required === true;

  const normalizedHumanDecision =
    String(
      governance?.human_review_decision ||
      governance?.human_review?.status ||
      ""
    ).toUpperCase();

  const humanReviewApproved =
    normalizedHumanDecision === "APPROVED";

  const humanReviewRejected =
    normalizedHumanDecision === "REJECTED";

  const humanReviewChangesRequested =
    normalizedHumanDecision === "REQUEST_CHANGES" ||
    normalizedHumanDecision === "CHANGES_REQUESTED";

  const controlledContinue =
    decision === "CONTROLLED_CONTINUE" &&
    (gate === "PASS" || gate === "PASSED") &&
    !humanReviewRequired;

  const governanceApproved =
    decision === "APPROVED" &&
    (gate === "PASSED" || gate === "PASS") &&
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
            : governanceApproved
              ? "APPROVED"
              : humanReviewRequired
                ? "HUMAN_REVIEW"
                : decision || "PENDING";

  const currentGovernanceGate =
    humanReviewApproved || governanceApproved
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
            : "NOT_REQUIRED";

  const currentHumanReviewDecision =
    governance?.human_review_decision ||
    governance?.human_review?.status ||
    null;

  const currentHumanReview =
    governance?.human_review || null;

  /*
   * Letztes Governance-Event aus dem aktuellen Run.
   */
  const latestGovernanceEvent =
    [...currentRun]
      .reverse()
      .find(
        (event) =>
          event.action === "GOVERNANCE_DECISION"
      ) || null;

  /*
   * Governance-Event für die Darstellung mit
   * dem aktuellen /agents/analyze-Ergebnis synchronisieren.
   *
   * Historische HUMAN_REVIEW / ACTIVE-Zustände
   * werden dadurch nicht fälschlich als aktueller
   * Zustand angezeigt.
   */
  const currentGovernanceEvent =
    latestGovernanceEvent
      ? {
          ...latestGovernanceEvent,
          status: currentGovernanceStatus,
          gate: currentGovernanceGate,
          decision: currentGovernanceStatus,
          reason:
            governance?.reason ||
            (
              controlledContinue
                ? "Keine Governance-Regel erfordert eine fachliche Prüfung."
                : "Eine qualifizierte fachliche Prüfung durch Mitarbeitende ist vor der weiteren Bearbeitung erforderlich."
            ),
          timestamp:
            governance?.timestamp ||
            latestGovernanceEvent.timestamp ||
            null,
          current: true
        }
      : {
          agent: "Governance Agent",
          action: "GOVERNANCE_DECISION",
          status: currentGovernanceStatus,
          gate: currentGovernanceGate,
          decision: currentGovernanceStatus,
          reason:
            governance?.reason ||
            (
              controlledContinue
                ? "Keine Governance-Regel erfordert eine fachliche Prüfung."
                : "Eine qualifizierte fachliche Prüfung durch Mitarbeitende ist vor der weiteren Bearbeitung erforderlich."
            ),
          timestamp:
            governance?.timestamp ||
            governance?.human_review?.timestamp ||
            null,
          current: true
        };

  /*
   * Human Review:
   *
   * Nicht mehr ausschließlich aus der historischen
   * Event-Reihenfolge ableiten.
   *
   * Wenn /agents/analyze/{caseId} eine abgeschlossene
   * fachliche Prüfung meldet, wird diese als aktueller
   * Human-Review-Zustand dargestellt.
   */
  const historicalHumanDecision =
    [...events]
      .reverse()
      .find(
        (event) =>
          event.action === "HUMAN_REVIEW_DECISION"
      ) || null;

  /*
   * Human Review nur dann als aktuelle fachliche Entscheidung
   * anzeigen, wenn tatsächlich eine aktuelle Entscheidung
   * vorliegt.
   *
   * Wichtig:
   * governance.timestamp darf hier NICHT als Timestamp der
   * Human-Review-Entscheidung verwendet werden. Dieser gehört
   * zur Governance-Entscheidung und kann zeitlich vor oder nach
   * der fachlichen Prüfung liegen.
   */
  const hasCurrentHumanDecision =
    humanReviewApproved ||
    humanReviewRejected ||
    humanReviewChangesRequested ||
    Boolean(currentHumanReviewDecision);

  const humanDecision =
    hasCurrentHumanDecision
      ? {
          ...(historicalHumanDecision || {}),
          ...(currentHumanReview || {}),
          agent:
            currentHumanReview?.agent ||
            historicalHumanDecision?.agent ||
            "Human Reviewer",
          action: "HUMAN_REVIEW_DECISION",
          status:
            currentHumanReviewDecision ||
            currentHumanReview?.status ||
            (humanReviewApproved
              ? "APPROVED"
              : humanReviewRejected
                ? "REJECTED"
                : humanReviewChangesRequested
                  ? "REQUEST_CHANGES"
                  : "APPROVED"),
          result:
            currentHumanReview?.result ||
            historicalHumanDecision?.result ||
            "Fachliche Prüfung abgeschlossen.",
          timestamp:
            currentHumanReview?.timestamp ||
            historicalHumanDecision?.timestamp ||
            null,
          current: true
        }
      : null;

  /*
   * Wenn keine aktuelle Human-Review-Entscheidung vorliegt,
   * darf auch keine alte APPROVED-Entscheidung als aktuell
   * dargestellt werden.
   */
  const visibleHumanDecision =
    hasCurrentHumanDecision
      ? humanDecision
      : null;

  /*
   * Wenn Human Review noch erforderlich ist,
   * keinen alten APPROVED-Entscheid als aktuell anzeigen.
   */
  const visibleEventCount =
    workflowEvents.length +
    (visibleHumanDecision ? 1 : 0);
  const formatTimestamp = (timestamp) => {
    if (!timestamp) {
      return "";
    }

    const date = new Date(timestamp);

    if (Number.isNaN(date.getTime())) {
      return String(timestamp);
    }

    return date.toLocaleString("de-DE", {
      dateStyle: "short",
      timeStyle: "medium",
    });
  };

  const parseResult = (result) => {
    if (!result) {
      return null;
    }

    if (typeof result === "object") {
      return result;
    }

    if (typeof result !== "string") {
      return String(result);
    }

    try {
      return JSON.parse(result);
    } catch {
      return result;
    }
  };

  const getDisplayResult = (result) => {
    const parsed = parseResult(result);

    if (!parsed) {
      return null;
    }

    if (
      typeof parsed === "object" &&
      !Array.isArray(parsed)
    ) {
      const preferredKeys = [
        "summary",
        "decision",
        "gate",
        "reason",
        "quality_status",
        "process",
        "risk_level",
        "priority",
        "human_review_required",
      ];

      const entries = preferredKeys
        .filter(
          (key) =>
            parsed[key] !== undefined &&
            parsed[key] !== null
        )
        .map((key) => ({
          key,
          value: parsed[key],
        }));

      if (entries.length > 0) {
        return (
          <div className="audit-details">
            {entries.map(({ key, value }) => (
              <div
                className="audit-detail-row"
                key={key}
              >
                <span className="audit-detail-label">
                  {key.replace(/_/g, " ")}
                </span>

                <span className="audit-detail-value">
                  {Array.isArray(value)
                    ? value.join(", ")
                    : String(value)}
                </span>
              </div>
            ))}
          </div>
        );
      }

      return null;
    }

    return (
      <div className="history-result">
        {String(parsed)}
      </div>
    );
  };

  const getHumanDecisionText = (event) => {
    if (!event) {
      return "—";
    }

    if (event.result) {
      return typeof event.result === "object"
        ? JSON.stringify(event.result)
        : String(event.result);
    }

    return "Fachliche Prüfung abgeschlossen.";
  };

  const renderEvent = (
    event,
    index,
    eventList
  ) => (
    <div
      className="history-event"
      key={`${event.timestamp || "event"}-${event.action || ""}-${index}`}
    >
      <div className="history-marker">
        <span className="history-dot" />

        {index < eventList.length - 1 && (
          <span className="history-line" />
        )}
      </div>

      <div className="history-content">
        <div className="history-top">
          <strong>
            {event.agent || "System"}
          </strong>

          {event.status && (
            <span className="status-badge">
              {event.status}
            </span>
          )}
        </div>

        <div className="history-action">
          {event.action || "EVENT"}
        </div>

        {getDisplayResult(event.result)}

        <div className="history-time">
          {formatTimestamp(event.timestamp)}
        </div>
      </div>
    </div>
  );

  const renderSection = (
    title,
    eventList,
    emptyText
  ) => (
    <div className="audit-group">
      <div className="audit-group-header">
        <span className="audit-group-title">
          {title}
        </span>

        <span className="audit-group-count">
          {eventList.length}
        </span>
      </div>

      {eventList.length > 0 ? (
        <div className="history-list">
          {eventList.map(
            (event, index) =>
              renderEvent(
                event,
                index,
                eventList
              )
          )}
        </div>
      ) : (
        <div className="audit-empty">
          {emptyText}
        </div>
      )}
    </div>
  );

  return (
    <section className="panel audit-trail">
      <div className="section-header">
        <div>
          <div className="panel-kicker">
            AUDIT TRAIL
          </div>

          <h3>
            Agent Execution History
          </h3>
        </div>

        <span className="ai-label">
          {visibleEventCount} EVENTS
        </span>
      </div>

      {renderSection(
        "WORKFLOW RUN",
        workflowEvents,
        "Noch keine Workflow-Events dokumentiert."
      )}

      <div className="audit-group">
        <div className="audit-group-header">
          <span className="audit-group-title">
            HUMAN DECISION
          </span>

          <span className="audit-group-count">
            {visibleHumanDecision
              ? 1
              : controlledContinue
                ? "—"
                : 0}
          </span>
        </div>

        {visibleHumanDecision ? (
          <div className="audit-review-summary">
            <div className="audit-review-label">
              FACHLICHE ENTSCHEIDUNG
            </div>

            <div className="audit-details">

              <div className="audit-detail-row">
                <span className="audit-detail-label">
                  Agent
                </span>

                <span className="audit-detail-value">
                  {visibleHumanDecision.agent ||
                    "Human Reviewer"}
                </span>
              </div>

              <div className="audit-detail-row">
                <span className="audit-detail-label">
                  Status
                </span>

                <span className="audit-detail-value">
                  {visibleHumanDecision.status ||
                    "APPROVED"}
                </span>
              </div>

              <div className="audit-detail-row">
                <span className="audit-detail-label">
                  Entscheidung
                </span>

                <span className="audit-detail-value">
                  {getHumanDecisionText(
                    visibleHumanDecision
                  )}
                </span>
              </div>

              <div className="audit-detail-row">
                <span className="audit-detail-label">
                  Zeitpunkt
                </span>

                <span className="audit-detail-value">
                  {formatTimestamp(
                    visibleHumanDecision.timestamp
                  )}
                </span>
              </div>

            </div>
          </div>
        ) : controlledContinue ? (
          <div className="audit-review-summary">
            <div className="audit-review-label">
              HUMAN REVIEW
            </div>

            <div className="audit-details">
              <div className="audit-detail-row">
                <span className="audit-detail-label">
                  Status
                </span>

                <span className="audit-detail-value">
                  NOT_REQUIRED
                </span>
              </div>

              <div className="audit-detail-row">
                <span className="audit-detail-label">
                  Ergebnis
                </span>

                <span className="audit-detail-value">
                  Keine fachliche Prüfung erforderlich.
                </span>
              </div>
            </div>
          </div>
        ) : (
          <div className="audit-empty">
            Noch keine fachliche Entscheidung dokumentiert.
          </div>
        )}
      </div>

      <div className="audit-group">
        <div className="audit-group-header">
          <span className="audit-group-title">
            GOVERNANCE GATE
          </span>

          <span className="audit-group-count">
            {currentGovernanceEvent ? 1 : 0}
          </span>
        </div>

        {currentGovernanceEvent ? (
          <div className="audit-review-summary">

            <div className="audit-review-label">
              GOVERNANCE AUDIT
            </div>

            <div className="audit-details">

              <div className="audit-detail-row">
                <span className="audit-detail-label">
                  Status
                </span>

                <span className="audit-detail-value">
                  {currentGovernanceGate}
                </span>
              </div>

              <div className="audit-detail-row">
                <span className="audit-detail-label">
                  Agent
                </span>

                <span className="audit-detail-value">
                  {currentGovernanceEvent.agent ||
                    "Governance Agent"}
                </span>
              </div>

              <div className="audit-detail-row">
                <span className="audit-detail-label">
                  Ergebnis
                </span>

                <span className="audit-detail-value">
                  {currentGovernanceStatus}
                </span>
              </div>

              <div className="audit-detail-row">
                <span className="audit-detail-label">
                  Zeitpunkt
                </span>

                <span className="audit-detail-value">
                  {formatTimestamp(
                    currentGovernanceEvent.timestamp
                  )}
                </span>
              </div>

              {currentGovernanceEvent.reason && (
                <div className="audit-detail-row">
                  <span className="audit-detail-label">
                    Begründung
                  </span>

                  <span className="audit-detail-value">
                    {currentGovernanceEvent.reason}
                  </span>
                </div>
              )}

            </div>
          </div>
        ) : (
          <div className="audit-empty">
            Governance-Gate wurde noch nicht passiert.
          </div>
        )}
      </div>
    </section>
  );
}

export default AuditTrail;
