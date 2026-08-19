function AuditTrail({ history = [] }) {
  /*
   * Der Audit-Log enthält historische Workflow-Durchläufe.
   * Für die UI zeigen wir pro Agent/Aktion nur den neuesten Zustand.
   *
   * Die vollständige Historie bleibt im Backend/Audit-Log erhalten.
   */

  const latestEvents = [];

  const seen = new Set();

  for (let i = history.length - 1; i >= 0; i--) {
    const event = history[i];

    const key = `${event.agent || ""}:${event.action || ""}`;

    if (!seen.has(key)) {
      seen.add(key);
      latestEvents.unshift(event);
    }
  }

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
          {latestEvents.length} EVENTS
        </span>

      </div>


      <div className="history-list">

        {latestEvents.map((event, index) => (

          <div
            className="history-event"
            key={`${event.timestamp}-${event.agent}-${event.action}`}
          >

            <div className="history-marker">

              <span className="history-dot" />

              {index < latestEvents.length - 1 && (
                <span className="history-line" />
              )}

            </div>


            <div className="history-content">

              <div className="history-top">

                <strong>
                  {event.agent}
                </strong>

                <span className="status-badge">
                  {event.status}
                </span>

              </div>


              <div className="history-action">
                {event.action}
              </div>


              {event.result && (
                <div className="history-result">
                  {event.result}
                </div>
              )}


              <div className="history-time">

                {event.timestamp
                  ? new Date(event.timestamp).toLocaleString("de-DE")
                  : ""}

              </div>

            </div>

          </div>

        ))}

      </div>

    </section>
  );
}

export default AuditTrail;
