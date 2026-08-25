from fastapi import APIRouter, HTTPException

from app.services.databricks_service import databricks_service


router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
)


INTEGER_FIELDS = {
    "total_cases",
    "open_cases",
    "high_priority_cases",
    "closed_cases",
    "total_categories",
    "sick_pay_cases",
}


def _rows_from_databricks_response(response: dict) -> list[dict]:
    """Convert Databricks SQL response into normal JSON rows."""

    columns = [
        column["name"]
        for column in response["manifest"]["schema"]["columns"]
    ]

    rows = response.get("result", {}).get("data_array", [])

    result = []

    for row in rows:
        item = dict(zip(columns, row))

        for field in INTEGER_FIELDS:
            if field in item and item[field] is not None:
                item[field] = int(item[field])

        result.append(item)

    return result


@router.get("/cases")
def case_analytics():
    try:
        response = databricks_service.query("""
            SELECT
                case_type,
                total_cases,
                open_cases,
                high_priority_cases,
                closed_cases
            FROM workspace.gold.case_analytics
            ORDER BY case_type
        """)

        return _rows_from_databricks_response(response)

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Databricks query failed: {exc}",
        )


@router.get("/sick-pay")
def sick_pay_analytics():
    try:
        response = databricks_service.query("""
            SELECT
                case_type,
                total_cases,
                open_cases,
                high_priority_cases
            FROM workspace.gold.sick_pay_analytics
        """)

        return _rows_from_databricks_response(response)

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Databricks query failed: {exc}",
        )


@router.get("/summary")
def case_summary():
    try:
        response = databricks_service.query("""
            SELECT
                total_cases,
                open_cases,
                high_priority_cases,
                closed_cases,
                total_categories,
                sick_pay_cases
            FROM workspace.gold.case_summary
        """)

        rows = _rows_from_databricks_response(response)

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

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Databricks query failed: {exc}",
        )
