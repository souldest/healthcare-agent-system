from fastapi import APIRouter, HTTPException

from backend.app.tools.databricks_tool import (
    get_case_analytics,
    get_case_summary,
    get_sick_pay_analytics,
)


router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
)


@router.get("/cases")
def case_analytics():
    try:
        return get_case_analytics()

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Databricks query failed: {exc}",
        )


@router.get("/sick-pay")
def sick_pay_analytics():
    try:
        return get_sick_pay_analytics()

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Databricks query failed: {exc}",
        )


@router.get("/summary")
def case_summary():
    try:
        return get_case_summary()

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Databricks query failed: {exc}",
        )
