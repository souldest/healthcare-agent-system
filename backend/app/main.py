from typing import Any
import json
import os
import urllib.request

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://banking:banking@localhost:5432/banking_poc",
)

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:1b",
)


engine: Engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


app = FastAPI(
    title="Bank Risk & Regulatory Analytics POC",
    version="1.3.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:4173",
        "http://localhost:8000",
        "http://localhost:8003",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def fetch_one(
    sql: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    with engine.connect() as conn:
        row = conn.execute(
            text(sql),
            params or {},
        ).mappings().first()

    return dict(row) if row else {}


def fetch_all(
    sql: str,
    params: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(sql),
            params or {},
        ).mappings().all()

    return [dict(row) for row in rows]


def ollama_generate(prompt: str) -> str:
    payload = json.dumps(
        {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 120,
                "temperature": 0.0,
            },
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(
        request,
        timeout=120,
    ) as response:
        data = json.loads(
            response.read().decode("utf-8")
        )

    return data.get("response", "").strip()


@app.get("/api/health")
def health() -> dict[str, str]:
    try:
        fetch_one("SELECT 1 AS ok")

        return {
            "status": "ok",
            "database": "postgresql",
        }

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"PostgreSQL unavailable: {exc}",
        ) from exc


@app.get("/api/risk/overview")
def risk_overview() -> dict[str, Any]:
    summary = fetch_one(
        """
        SELECT
          COUNT(*) AS customers,

          ROUND(
            SUM(credit_exposure)::numeric,
            2
          ) AS total_exposure,

          COUNT(*) FILTER (
            WHERE risk_category = 'High'
          ) AS high_risk_customers,

          ROUND(
            100.0 * AVG(
              CASE
                WHEN default_flag THEN 1.0
                ELSE 0.0
              END
            )::numeric,
            2
          ) AS default_rate_pct,

          ROUND(
            100.0 *
            SUM(
              CASE
                WHEN risk_category = 'High'
                THEN credit_exposure
                ELSE 0
              END
            )::numeric
            /
            NULLIF(
              SUM(credit_exposure)::numeric,
              0
            ),
            2
          ) AS high_risk_exposure_pct

        FROM customer_risk
        """
    )

    distribution = fetch_all(
        """
        SELECT
          risk_category,
          COUNT(*) AS customers,

          ROUND(
            SUM(credit_exposure)::numeric,
            2
          ) AS exposure

        FROM customer_risk

        GROUP BY risk_category

        ORDER BY
          CASE risk_category
            WHEN 'High' THEN 1
            WHEN 'Medium' THEN 2
            ELSE 3
          END
        """
    )

    return {
        "summary": summary,
        "distribution": distribution,
    }


@app.get("/api/risk/by-country")
def risk_by_country() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT
          country,
          COUNT(*) AS customers,

          ROUND(
            SUM(credit_exposure)::numeric,
            2
          ) AS exposure,

          ROUND(
            100.0 * AVG(
              CASE
                WHEN default_flag THEN 1.0
                ELSE 0.0
              END
            )::numeric,
            2
          ) AS default_rate_pct,

          ROUND(
            AVG(risk_score)::numeric,
            1
          ) AS avg_risk_score

        FROM customer_risk

        GROUP BY country

        ORDER BY exposure DESC
        """
    )


@app.get("/api/risk/high-risk")
def high_risk(
    limit: int = 20,
) -> list[dict[str, Any]]:

    limit = max(
        1,
        min(limit, 100),
    )

    return fetch_all(
        """
        SELECT
          customer_id,
          customer_name,
          country,
          product,
          credit_exposure,
          risk_score,
          default_flag,
          risk_reason

        FROM customer_risk

        WHERE risk_category = 'High'

        ORDER BY
          risk_score DESC,
          credit_exposure DESC

        LIMIT :limit
        """,
        {"limit": limit},
    )


@app.get("/api/data-quality")
def data_quality() -> dict[str, Any]:
    checks = fetch_all(
        """
        SELECT
          check_name,
          status,
          issue_count,
          details

        FROM data_quality_checks

        ORDER BY
          severity DESC,
          check_name
        """
    )

    total_records = fetch_one(
        "SELECT COUNT(*) AS count FROM customer_risk"
    )["count"]

    issue_records = sum(
        row["issue_count"]
        for row in checks
    )

    score = max(
        0.0,
        round(
            100.0
            - (
                issue_records
                / max(total_records, 1)
                * 100
            ),
            2,
        ),
    )

    return {
        "score_pct": score,
        "total_records": total_records,
        "issue_records": issue_records,
        "checks": checks,
        "note": (
            "Demonstration metric for the POC; "
            "not a regulatory data-quality methodology."
        ),
    }


@app.get("/api/reporting/summary")
def reporting_summary() -> dict[str, Any]:
    overview = fetch_one(
        """
        SELECT
          COUNT(*) AS records,

          ROUND(
            SUM(credit_exposure)::numeric,
            2
          ) AS exposure,

          ROUND(
            SUM(
              CASE
                WHEN default_flag
                THEN credit_exposure
                ELSE 0
              END
            )::numeric,
            2
          ) AS defaulted_exposure,

          ROUND(
            SUM(
              CASE
                WHEN risk_category = 'High'
                THEN credit_exposure
                ELSE 0
              END
            )::numeric,
            2
          ) AS high_risk_exposure

        FROM customer_risk
        """
    )

    dq = fetch_one(
        """
        SELECT
          COUNT(*) AS checks,

          COUNT(*) FILTER (
            WHERE status = 'PASS'
          ) AS passed

        FROM data_quality_checks
        """
    )

    overview.update(
        {
            "data_quality_checks": dq["checks"],
            "passed_checks": dq["passed"],
        }
    )

    return overview


@app.get("/api/customers/{customer_id}")
def customer_detail(
    customer_id: str,
) -> dict[str, Any]:

    row = fetch_one(
        """
        SELECT
          customer_id,
          customer_name,
          country,
          product,
          credit_exposure,
          risk_score,
          risk_category,
          default_flag,
          income,
          transaction_count_90d,
          unusual_transaction_flag,
          risk_reason

        FROM customer_risk

        WHERE customer_id = :customer_id
        """,
        {"customer_id": customer_id},
    )

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    return row


@app.get("/api/ai/risk-analysis")
def ai_risk_analysis() -> dict[str, Any]:
    try:
        overview = risk_overview()
        countries = risk_by_country()
        quality = data_quality()
        high_risk_rows = high_risk()

        summary = overview.get("summary", {})
        checks = quality.get("checks", [])

        sorted_countries = sorted(
            countries,
            key=lambda row: float(row.get("default_rate_pct") or 0),
            reverse=True,
        )

        top_country = sorted_countries[0] if sorted_countries else {}

        high_risk_defaults = [
            row
            for row in high_risk_rows
            if row.get("default_flag") is True
        ]

        dq_failures = [
            row
            for row in checks
            if row.get("status") != "PASS"
        ]

        # ---------------------------------------------------------
        # Deterministische Findings
        # ---------------------------------------------------------

        finding_1 = (
            f"{top_country.get('country', '—')} weist mit "
            f"{top_country.get('default_rate_pct', '—')}% die höchste "
            f"Default Rate der betrachteten Länder auf "
            f"({top_country.get('customers', '—')} Kunden)."
        )

        finding_2 = (
            f"{summary.get('high_risk_customers', '—')} Kunden sind als "
            f"High Risk klassifiziert. Die gesamte Exposure beträgt "
            f"{summary.get('total_exposure', '—')} EUR."
        )

        finding_3 = (
            f"Es bestehen {quality.get('issue_records', 0)} problematische "
            f"Records bei einer Data Quality von "
            f"{quality.get('score_pct', '—')}%."
        )

        findings = [
            finding_1,
            finding_2,
            finding_3,
        ]

        # ---------------------------------------------------------
        # Deterministische Recommended Actions
        # ---------------------------------------------------------

        actions = [
            (
                f"{top_country.get('country', '—')} und die dortige "
                f"Default Rate von "
                f"{top_country.get('default_rate_pct', '—')}% gezielt "
                f"weiter untersuchen."
            ),
            (
                "High-Risk-Fälle priorisieren und insbesondere Fälle "
                "mit gleichzeitig hohem Risk Score und Default Flag prüfen."
            ),
            (
                "Die identifizierten Data-Quality-Probleme bereinigen "
                "und anschließend die DQ-Prüfung erneut ausführen."
            ),
        ]

        # ---------------------------------------------------------
        # Ollama erzeugt die Management Summary
        # ---------------------------------------------------------

        prompt = f"""
Du bist Risk Analyst in einer Bank.

Erstelle eine kurze Management Summary auf Deutsch.

REGELN:
- Maximal 3 Sätze.
- Keine Überschrift.
- Keine Aufzählung.
- Verwende ausschließlich die gelieferten Fakten.
- Erfinde keine Kennzahlen.
- Verändere keine Kennzahlen.
- Keine zusätzlichen Länder oder Kunden.
- Die Daten sind synthetische POC-Daten.
- Keine Anlageberatung.
- Keine regulatorische Entscheidung.
- Gib ausschließlich die Management Summary zurück.

FAKTEN:

Kunden: {summary.get("customers")}
Gesamtexposure: {summary.get("total_exposure")} EUR
Default Rate: {summary.get("default_rate_pct")}%
High-Risk Kunden: {summary.get("high_risk_customers")}
High-Risk Exposure: {summary.get("high_risk_exposure_pct")}%

Land mit höchster Default Rate:
{top_country.get("country", "—")}

Default Rate dieses Landes:
{top_country.get("default_rate_pct", "—")}%

Kunden in diesem Land:
{top_country.get("customers", "—")}

Data Quality:
{quality.get("score_pct", "—")}%

Problematische Records:
{quality.get("issue_records", 0)}

Fehlgeschlagene Checks:
{len(dq_failures)}

High-Risk Defaults:
{len(high_risk_defaults)}

Verbindliche Fakten:

{finding_1}

{finding_2}

{finding_3}
"""

        analysis = ollama_generate(prompt)

        if not analysis:
            analysis = (
                f"Das interne Banking-Analytics-POC umfasst "
                f"{summary.get('customers', '—')} Kunden mit einer "
                f"Gesamtexposure von "
                f"{summary.get('total_exposure', '—')} EUR und einer "
                f"Default Rate von "
                f"{summary.get('default_rate_pct', '—')}%."
            )

        return {
            "status": "ok",
            "model": OLLAMA_MODEL,
            "generator": "ollama",
            "analysis": analysis,
            "findings": findings,
            "recommended_actions": actions,
            "data_quality": {
                "score_pct": quality.get("score_pct"),
                "issue_records": quality.get("issue_records"),
                "failed_checks": len(dq_failures),
            },
        }

    except Exception as exc:
        return {
            "status": "error",
            "model": OLLAMA_MODEL,
            "generator": "ollama",
            "analysis": "AI-Analyse konnte nicht ausgeführt werden.",
            "detail": str(exc),
        }
