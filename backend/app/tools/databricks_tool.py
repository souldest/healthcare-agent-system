import json
import os
import subprocess
from typing import Any


PROFILE = os.getenv("DATABRICKS_PROFILE", "healthcare-bkk")
WAREHOUSE_ID = os.getenv("DATABRICKS_WAREHOUSE_ID", "e7d4c32260d73e76")
CATALOG = os.getenv("DATABRICKS_CATALOG", "workspace")
SCHEMA = os.getenv("DATABRICKS_SCHEMA", "gold")


def execute_databricks_sql(statement: str) -> dict[str, Any]:
    payload = {
        "warehouse_id": WAREHOUSE_ID,
        "catalog": CATALOG,
        "schema": SCHEMA,
        "statement": statement,
        "wait_timeout": "30s",
    }

    result = subprocess.run(
        [
            "databricks",
            "api",
            "post",
            "/api/2.0/sql/statements",
            "--profile",
            PROFILE,
            "--json",
            json.dumps(payload),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    response = json.loads(result.stdout)

    if response.get("status", {}).get("state") != "SUCCEEDED":
        raise RuntimeError(f"Databricks SQL failed: {response}")

    return response


def _response_to_rows(response: dict[str, Any]) -> list[dict[str, Any]]:
    columns = response["manifest"]["schema"]["columns"]
    rows = response["result"]["data_array"]
    names = [column["name"] for column in columns]

    return [dict(zip(names, row)) for row in rows]


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
