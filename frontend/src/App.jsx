import React, { useEffect, useState } from 'react';

export default function App({ API }) {
  const [overview, setOverview] = useState(null);
  const [countries, setCountries] = useState([]);
  const [highRisk, setHighRisk] = useState([]);
  const [quality, setQuality] = useState(null);

  const [aiAnalysis, setAiAnalysis] = useState('');
  const [aiFindings, setAiFindings] = useState([]);
  const [aiActions, setAiActions] = useState([]);
  const [aiModel, setAiModel] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        const responses = await Promise.all([
          fetch(`${API}/risk/overview`),
          fetch(`${API}/risk/by-country`),
          fetch(`${API}/risk/high-risk`),
          fetch(`${API}/data-quality`),
        ]);

        if (responses.some((response) => !response.ok)) {
          throw new Error('Backend API nicht erreichbar');
        }

        const [
          overviewData,
          countriesData,
          highRiskData,
          qualityData,
        ] = await Promise.all(
          responses.map((response) => response.json())
        );

        setOverview(overviewData);
        setCountries(countriesData);
        setHighRisk(highRiskData);
        setQuality(qualityData);
      } catch (err) {
        console.error(err);
        setError(err.message);
      }
    }

    loadData();
  }, [API]);

  const money = (value) =>
    Number(value || 0).toLocaleString('de-DE', {
      style: 'currency',
      currency: 'EUR',
      maximumFractionDigits: 0,
    });

  async function runAiAnalysis() {
    setAiLoading(true);
    setAiAnalysis('');
    setAiFindings([]);
    setAiActions([]);
    setAiModel('');

    try {
      const response = await fetch(`${API}/ai/risk-analysis`);

      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || 'AI-Service nicht erreichbar');
      }

      const data = await response.json();

      if (data.status !== 'ok') {
        throw new Error(
          data.detail || 'AI-Analyse fehlgeschlagen'
        );
      }

      setAiAnalysis(data.analysis || '');
      setAiFindings(
        Array.isArray(data.findings) ? data.findings : []
      );
      setAiActions(
        Array.isArray(data.recommended_actions)
          ? data.recommended_actions
          : []
      );
      setAiModel(data.model || '');
    } catch (err) {
      console.error(err);
      setAiAnalysis(
        `AI-Analyse konnte nicht ausgeführt werden: ${err.message}`
      );
    } finally {
      setAiLoading(false);
    }
  }

  if (error) {
    return (
      <main className="app">
        <div className="error">
          <strong>Backend nicht erreichbar</strong>
          <p>{error}</p>
        </div>
      </main>
    );
  }

  if (!overview || !quality) {
    return (
      <main className="app">
        <div className="loading">
          Banking Analytics POC wird geladen …
        </div>
      </main>
    );
  }

  const summary = overview.summary || {};
  const distribution = overview.distribution || [];

  const maxExposure = Math.max(
    ...distribution.map(
      (item) => Number(item.exposure || 0)
    ),
    1
  );

  return (
    <main className="app">
      <header className="topbar">
        <div>
          <div className="eyebrow">
            Banking Analytics POC
          </div>

          <h1>Risk & Regulatory Analytics</h1>

          <p>
            Data Quality → Risk KPIs → API → AI Analytics
          </p>
        </div>

        <button
          onClick={runAiAnalysis}
          disabled={aiLoading}
        >
          {aiLoading
            ? 'AI analysiert …'
            : 'AI Risk Analysis'}
        </button>
      </header>

      <section>
        <div className="cards">
          <div className="kpi">
            <span>Customers</span>
            <strong>
              {summary.customers ?? '—'}
            </strong>
          </div>

          <div className="kpi">
            <span>Total Exposure</span>
            <strong>
              {money(summary.total_exposure)}
            </strong>
          </div>

          <div className="kpi">
            <span>High-Risk Customers</span>
            <strong>
              {summary.high_risk_customers ?? '—'}
            </strong>
          </div>

          <div className="kpi">
            <span>Default Rate</span>
            <strong>
              {summary.default_rate_pct != null
                ? `${summary.default_rate_pct}%`
                : '—'}
            </strong>
          </div>
        </div>
      </section>

      <section className="grid two">
        <div className="panel">
          <div className="panel-title">
            Risk distribution
          </div>

          {distribution.map((item) => {
            const width =
              (Number(item.exposure || 0) /
                maxExposure) *
              100;

            const riskClass =
              item.risk_category?.toLowerCase() || '';

            return (
              <div
                className="bar-row"
                key={item.risk_category}
              >
                <div className="bar-label">
                  <strong>
                    {item.risk_category}
                  </strong>

                  <span>
                    {item.customers} Customers ·{' '}
                    {money(item.exposure)}
                  </span>
                </div>

                <div className="track">
                  <div
                    className={`bar ${riskClass}`}
                    style={{
                      width: `${width}%`,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        <div className="panel">
          <div className="panel-title">
            Data quality
          </div>

          <div className="dq-score">
            {quality.score_pct}%
          </div>

          <div className="dq-sub">
            {quality.issue_records} problematische
            Records von {quality.total_records}
          </div>

          <div className="mini-grid">
            {(quality.checks || []).map((check) => (
              <div
                className="check"
                key={check.check_name}
              >
                <strong>
                  {check.check_name}
                </strong>

                <strong
                  className={
                    check.status === 'PASS'
                      ? 'pass'
                      : 'fail'
                  }
                >
                  {check.status}
                </strong>

                <small>{check.details}</small>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="panel">
        <div className="panel-title">
          Risk by country
        </div>

        {(countries || []).map((country) => (
          <div
            className="country-row"
            key={country.country}
          >
            <div>
              <strong>
                {country.country}
              </strong>

              <span>
                {country.customers} Customers ·
                Default Rate{' '}
                {country.default_rate_pct}%
              </span>
            </div>

            <div className="country-meter">
              <div className="track">
                <div
                  className="bar"
                  style={{
                    width: `${Math.min(
                      Number(
                        country.avg_risk_score || 0
                      ),
                      100
                    )}%`,
                  }}
                />
              </div>

              <strong>
                Risk {country.avg_risk_score}
              </strong>
            </div>
          </div>
        ))}
      </section>

      <section className="panel ai-panel">
        <div className="ai-header">
          <div>
            <div className="panel-title">
              AI Risk Analysis
            </div>

            {aiModel && (
              <small className="ai-model">
                Model: {aiModel}
              </small>
            )}
          </div>

          {aiAnalysis && !aiLoading && (
            <span className="ai-status">
              Analysis completed
            </span>
          )}
        </div>

        {!aiAnalysis &&
          aiFindings.length === 0 &&
          !aiLoading && (
            <p>
              Starte die AI Risk Analysis, um die
              aktuellen Risk-KPIs, Data-Quality-Ergebnisse
              und Länder-Risiken automatisch analysieren
              zu lassen.
            </p>
          )}

        {aiLoading && (
          <div className="loading">
            Ollama analysiert die Risk-Daten …
          </div>
        )}

        {!aiLoading &&
          aiFindings.length > 0 && (
            <div className="ai-section">
              <h3>Key Risk Findings</h3>

              <div className="ai-list">
                {aiFindings.map((finding, index) => (
                  <div
                    className="ai-item"
                    key={`finding-${index}`}
                  >
                    <div className="ai-number">
                      {index + 1}
                    </div>

                    <div>{finding}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

        {!aiLoading &&
          aiActions.length > 0 && (
            <div className="ai-section">
              <h3>Recommended Actions</h3>

              <div className="ai-list">
                {aiActions.map((action, index) => (
                  <div
                    className="ai-item action"
                    key={`action-${index}`}
                  >
                    <div className="ai-number">
                      {index + 1}
                    </div>

                    <div>{action}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

        {!aiLoading &&
          aiAnalysis &&
          aiFindings.length === 0 &&
          aiActions.length === 0 && (
            <div
              style={{
                whiteSpace: 'pre-wrap',
                lineHeight: 1.6,
              }}
            >
              {aiAnalysis}
            </div>
          )}
      </section>

      <section className="panel">
        <div className="panel-title">
          High-risk cases
        </div>

        {highRisk.length === 0 ? (
          <p>Keine High-Risk-Fälle.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Kunde</th>
                <th>Land</th>
                <th>Produkt</th>
                <th>Score</th>
                <th>Exposure</th>
                <th>Grund</th>
              </tr>
            </thead>

            <tbody>
              {highRisk
                .slice(0, 20)
                .map((item, index) => (
                  <tr
                    key={
                      item.customer_id ?? index
                    }
                  >
                    <td>
                      {item.customer_id ?? '—'}
                    </td>

                    <td>
                      {item.customer_name ?? '—'}
                    </td>

                    <td>
                      {item.country ?? '—'}
                    </td>

                    <td>
                      {item.product ?? '—'}
                    </td>

                    <td className="score">
                      {item.risk_score ?? '—'}
                    </td>

                    <td>
                      {item.credit_exposure != null
                        ? money(
                            item.credit_exposure
                          )
                        : '—'}
                    </td>

                    <td>
                      {item.risk_reason ?? '—'}
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        )}
      </section>
    </main>
  );
}
