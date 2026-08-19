import { useState } from "react";

const API_BASE = "http://localhost:8000";

function MemberPortal() {
  const [insuranceNumber, setInsuranceNumber] = useState("");
  const [patient, setPatient] = useState(null);
  const [cases, setCases] = useState([]);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [chatLoading, setChatLoading] = useState(false);
  const [error, setError] = useState(null);

  async function login() {
    const number = insuranceNumber.trim();

    if (!number) {
      setError("Bitte geben Sie Ihre Versicherungsnummer ein.");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const patientResponse = await fetch(
        `${API_BASE}/member/${encodeURIComponent(number)}`
      );

      if (!patientResponse.ok) {
        const data = await patientResponse.json();
        throw new Error(
          data.detail || "Versicherter konnte nicht gefunden werden."
        );
      }

      const patientData = await patientResponse.json();

      const casesResponse = await fetch(
        `${API_BASE}/member/${encodeURIComponent(number)}/cases`
      );

      if (!casesResponse.ok) {
        throw new Error("Vorgänge konnten nicht geladen werden.");
      }

      const casesData = await casesResponse.json();

      setPatient(patientData.patient);
      setCases(casesData.cases || []);
      setMessages([]);
    } catch (err) {
      setPatient(null);
      setCases([]);
      setError(
        err.message || "Anmeldung konnte nicht durchgeführt werden."
      );
    } finally {
      setLoading(false);
    }
  }

  async function sendQuestion() {
    const text = question.trim();

    if (!text || !patient) {
      return;
    }

    try {
      setChatLoading(true);
      setError(null);

      setMessages((current) => [
        ...current,
        {
          role: "user",
          text,
        },
      ]);

      setQuestion("");

      const response = await fetch(
        `${API_BASE}/member/${encodeURIComponent(
          patient.insurance_number
        )}/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question: text,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Die Anfrage konnte nicht verarbeitet werden."
        );
      }

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          text: data.answer,
          requiresHuman: data.requires_human,
        },
      ]);
    } catch (err) {
      setError(
        err.message || "Die Anfrage konnte nicht verarbeitet werden."
      );
    } finally {
      setChatLoading(false);
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendQuestion();
    }
  }

  if (!patient) {
    return (
      <div className="member-portal">
        <div className="member-login">
          <div className="panel-kicker">
            BKK VERSICHERTENPORTAL
          </div>

          <h1>
            Willkommen
          </h1>

          <p>
            Melden Sie sich mit Ihrer Versicherungsnummer an,
            um Ihren persönlichen Bereich zu öffnen.
          </p>

          {error && (
            <div className="error-banner">
              {error}
            </div>
          )}

          <label>
            Versicherungsnummer
          </label>

          <input
            type="text"
            value={insuranceNumber}
            onChange={(event) =>
              setInsuranceNumber(event.target.value)
            }
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                login();
              }
            }}
            placeholder="z. B. BKK123456"
          />

          <button
            type="button"
            onClick={login}
            disabled={loading}
          >
            {loading
              ? "Anmeldung wird geprüft ..."
              : "Zum persönlichen Bereich"}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="member-portal">
      <div className="member-header">
        <div>
          <div className="panel-kicker">
            BKK VERSICHERTENPORTAL
          </div>

          <h1>
            Hallo {patient.first_name} {patient.last_name}
          </h1>

          <p>
            Wie kann ich Ihnen helfen?
          </p>
        </div>

        <div className="member-number">
          Versicherungsnummer
          <strong>
            {patient.insurance_number}
          </strong>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      <div className="member-grid">
        <section className="member-chat">
          <div className="panel-kicker">
            DIGITALER BKK-ASSISTENT
          </div>

          <h2>
            Wie kann ich Ihnen helfen?
          </h2>

          <div className="member-suggestions">
            <button
              type="button"
              onClick={() =>
                setQuestion(
                  "Wie kann ich eine Rechnung einreichen?"
                )
              }
            >
              Rechnung einreichen
            </button>

            <button
              type="button"
              onClick={() =>
                setQuestion(
                  "Welche Unterlagen brauche ich für einen Antrag?"
                )
              }
            >
              Benötigte Unterlagen
            </button>

            <button
              type="button"
              onClick={() =>
                setQuestion(
                  "Was bedeutet der Status meines Antrags?"
                )
              }
            >
              Bearbeitungsstatus
            </button>
          </div>

          <div className="member-messages">
            {messages.length === 0 && (
              <div className="member-empty-chat">
                Stellen Sie Ihre Frage. Bei individuellen oder
                sensiblen Entscheidungen kann ein BKK-Mitarbeiter
                hinzugezogen werden.
              </div>
            )}

            {messages.map((message, index) => (
              <div
                key={index}
                className={
                  message.role === "user"
                    ? "member-message user"
                    : "member-message assistant"
                }
              >
                <span>
                  {message.role === "user"
                    ? "Sie"
                    : "BKK-Assistent"}
                </span>

                <p>
                  {message.text}
                </p>

                {message.requiresHuman && (
                  <div className="member-escalation">
                    Übergabe an einen BKK-Mitarbeiter erforderlich.
                  </div>
                )}
              </div>
            ))}

            {chatLoading && (
              <div className="member-message assistant">
                <span>BKK-Assistent</span>
                <p>
                  Ihre Anfrage wird geprüft ...
                </p>
              </div>
            )}
          </div>

          <div className="member-chat-input">
            <textarea
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder="Ihre Frage ..."
              rows={3}
            />

            <button
              type="button"
              onClick={sendQuestion}
              disabled={
                chatLoading || !question.trim()
              }
            >
              Frage stellen
            </button>
          </div>
        </section>

        <section className="member-cases">
          <div className="panel-kicker">
            MEINE VORGÄNGE
          </div>

          <h2>
            Bearbeitungsstand
          </h2>

          {cases.length === 0 ? (
            <div className="member-empty">
              Aktuell sind keine Vorgänge hinterlegt.
            </div>
          ) : (
            <div className="member-case-list">
              {cases.map((item) => (
                <div
                  className="member-case"
                  key={item.case_id}
                >
                  <div>
                    <span>
                      VORGANG
                    </span>

                    <strong>
                      #{item.case_id}
                    </strong>
                  </div>

                  <span className="member-case-status">
                    {item.status}
                  </span>
                </div>
              ))}
            </div>
          )}

          <div className="member-notice">
            <strong>
              Hinweis
            </strong>

            <span>
              Die KI unterstützt bei allgemeinen Fragen.
              Individuelle medizinische oder
              leistungsbezogene Entscheidungen werden
              durch BKK-Mitarbeiter geprüft.
            </span>
          </div>
        </section>
      </div>
    </div>
  );
}

export default MemberPortal;

