import json
import os
import subprocess
from typing import Any


PROFILE = os.getenv("DATABRICKS_PROFILE", "healthcare-bkk")
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "e7d4c32260d73e76")
CATALOG = os.getenv("DATABRICKS_CATALOG", "workspace")
SCHEMA = os.getenv("DATABRICKS_SCHEMA", "gold")


CI = os.getenv("CI", "").lower() == "true"


CI_RESULTS = {
    "case_analytics": [
        {
            "case_type": "General",
            "total_cases": 10,
            "open_cases": 4,
            "high_priority_cases": 2,
            "closed_cases": 6,
        },
        {
            "case_type": "Sick Pay",
            "total_cases": 5,
            "open_cases": 2,
            "high_priority_cases": 1,
            "closed_cases": 3,
        },
    ],
    "sick_pay_analytics": [
        {
            "case_type": "Sick Pay",
            "total_cases": 5,
            "open_cases": 2,
            "high_priority_cases": 1,
            "oldest_case": "2026-01-01",
            "newest_case": "2026-08-01",
        },
    ],
    "case_summary": [
        {
            "total_cases": 15,
            "open_cases": 6,
            "high_priority_cases": 3,
            "closed_cases": 9,
            "total_categories": 2,
            "sick_pay_cases": 5,
        }
    ],
}


def _ci_response(statement: str) -> dict[str, Any]:
    sql = statement.lower()

    if "case_summary" in sql:
        rows = CI_RESULTS["case_summary"]
        columns = [
            "total_cases",
            "open_cases",
            "high_priority_cases",
            "closed_cases",
            "total_categories",
            "sick_pay_cases",
        ]

    elif "sick_pay_analytics" in sql:
        rows = CI_RESULTS["sick_pay_analytics"]
        columns = [
            "case_type",
            "total_cases",
            "open_cases",
            "high_priority_cases",
            "oldest_case",
            "newest_case",
        ]

    elif "case_analytics" in sql:
        rows = CI_RESULTS["case_analytics"]
        columns = [
            "case_type",
            "total_cases",
            "open_cases",
            "high_priority_cases",
            "closed_cases",
        ]

    else:
        raise RuntimeError(
            f"No CI Databricks fixture for SQL: {statement}"
        )

    return {
        "manifest": {
            "schema": {
                "columns": [
                    {"name": column}
                    for column in columns
                ]
            }
        },
        "result": {
            "data_array": [
                [row.get(column) for column in columns]
                for row in rows
            ]
        },
        "status": {
            "state": "SUCCEEDED"
        },
    }


def execute_databricks_sql(statement: str) -> dict[str, Any]:
    if CI:
        return _ci_response(statement)

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
