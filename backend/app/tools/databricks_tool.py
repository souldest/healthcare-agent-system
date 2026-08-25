import json
import os
import subprocess
from typing import Any


PROFILE = os.getenv("DATABRICKS_PROFILE", "healthcare-bkk")
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "e7d4c32260d73e76")
CATALOG = os.getenv("DATABRICKS_CATALOG", "workspace")
SCHEMA = os.getenv("DATABRICKS_SCHEMA", "gold")


# Deterministische Demo-Daten für CI.
# Produktion verwendet weiterhin Databricks.
CI_CASE_ANALYTICS = [
    {
        "case_type": "CARDIOLOGY",
        "total_cases": 2,
        "open_cases": 2,
        "high_priority_cases": 2,
        "closed_cases": 0,
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
    "open_cases": 4,
    "high_priority_cases": 2,
    "closed_cases": 0,
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
    if os.getenv("CI", "").lower() == "true":
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
    if os.getenv("CI", "").lower() == "true":
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
    if os.getenv("CI", "").lower() == "true":
        return CI_CASE_SUMMARY

    case_analytics = get_case_analytics()
    sick_pay = get_sick_pay_analytics()

    return {
        "total_cases": sum(
            item["total_cases"]
            for item in case_analytics
        ),
        "open_cases": sum(
            item["open_cases"]
            for item in case_analytics
        ),
        "high_priority_cases": sum(
            item["high_priority_cases"]
            for item in case_analytics
        ),
        "closed_cases": sum(
            item["closed_cases"]
            for item in case_analytics
        ),
        "total_categories": len(case_analytics),
        "sick_pay_cases": sum(
            item["total_cases"]
            for item in sick_pay
        ),
    }
