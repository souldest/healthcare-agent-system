import json
import os
import subprocess
from typing import Any


PROFILE = os.getenv("DATABRICKS_PROFILE", "healthcare-bkk")
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "e7d4c32260d73e76")
CATALOG = os.getenv("DATABRICKS_CATALOG", "workspace")
SCHEMA = os.getenv("DATABRICKS_SCHEMA", "gold")


# CI verwendet deterministische Demo-Daten statt einer echten
# Databricks-Verbindung. Produktion verwendet weiterhin Databricks.
CI_CASE_ANALYTICS = [
    {
        "case_type": "CARDIOLOGY",
        "total_cases": 2,
        "open_cases": 1,
        "high_priority_cases": 1,
        "closed_cases": 1,
    },
    {
        "case_type": "GENERAL",
        "total_cases": 1,
        "open_cases": 1,
        "high_priority_cases": 0,
        "closed_cases": 0,
    },
    {
        "case_type": "SICK_PAY",
        "total_cases": 1,
        "open_cases": 1,
        "high_priority_cases": 0,
        "closed_cases": 0,
    },
]

CI_SICK_PAY_ANALYTICS = [
    {
        "case_type": "SICK_PAY",
        "total_cases": 1,
        "open_cases": 1,
        "high_priority_cases": 0,
        "oldest_case": "2026-01-01",
        "newest_case": "2026-01-01",
    },
]

CI_CASE_SUMMARY = {
    "total_cases": 4,
    "open_cases": 3,
    "high_priority_cases": 1,
    "closed_cases": 1,
    "total_categories": 3,
    "sick_pay_cases": 1,
}


def execute_databricks_sql(statement: str) -> dict[str, Any]:
    payload = {
        "warehouse_id": WAREHOUSE_ID,
        "catalog": CATALOG,
        "schema": SCHEMA,
        "statement": statement,
        "wait_timeout": "30s",
    }

    command = [
        "databricks",
        "api",
        "post",
        "/api/2.0/sql/statements",
        "--json",
        json.dumps(payload),
    ]

    if not os.getenv("DATABRICKS_TOKEN"):
        command.extend(["--profile", PROFILE])

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    response = json.loads(result.stdout)

    if response.get("status", {}).get("state") != "SUCCEEDED":
        raise RuntimeError(
            f"Databricks SQL failed: {response}"
        )

    return response


def _response_to_rows(
    response: dict[str, Any],
) -> list[dict[str, Any]]:
    columns = response["manifest"]["schema"]["columns"]
    rows = response["result"]["data_array"]
    names = [column["name"] for column in columns]

    return [
        dict(zip(names, row))
        for row in rows
    ]


def get_case_analytics() -> list[dict[str, Any]]:
    if os.getenv("CI") == "true":
        return CI_CASE_ANALYTICS

    response = execute_databricks_sql(
        """
        SELECT
            case_type,
            total_cases,
            open_cases,
            high_priority_cases,
            closed_cases
        FROM case_analytics
        ORDER BY case_type
        """
    )

    return _response_to_rows(response)


def get_sick_pay_analytics() -> list[dict[str, Any]]:
    if os.getenv("CI") == "true":
        return CI_SICK_PAY_ANALYTICS

    response = execute_databricks_sql(
        """
        SELECT
            case_type,
            total_cases,
            open_cases,
            high_priority_cases,
            oldest_case,
            newest_case
        FROM sick_pay_analytics
        ORDER BY case_type
        """
    )

    return _response_to_rows(response)


def get_case_summary() -> dict[str, Any]:
    if os.getenv("CI") == "true":
        return CI_CASE_SUMMARY

    response = execute_databricks_sql(
        """
        SELECT
            total_cases,
            open_cases,
            high_priority_cases,
            closed_cases,
            total_categories,
            sick_pay_cases
        FROM case_summary
        """
    )

    rows = _response_to_rows(response)

    if not rows:
        return {
            "total_cases": 0,
            "open_cases": 0,
            "high_priority_cases": 0,
            "closed_cases": 0,
            "total_categories": 0,
            "sick_pay_cases": 0,
        }

    return rows[0]
