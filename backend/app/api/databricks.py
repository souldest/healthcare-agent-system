from fastapi import APIRouter

from backend.app.tools.databricks_tool import (
    get_case_analytics,
    get_sick_pay_analytics,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Databricks Analytics"],
)


@router.get("/cases")
def case_analytics():
    return {
        "source": "databricks",
        "table": "workspace.gold.case_analytics",
        "data": get_case_analytics(),
    }


@router.get("/sick-pay")
def sick_pay_analytics():
    return {
        "source": "databricks",
        "table": "workspace.gold.sick_pay_analytics",
        "data": get_sick_pay_analytics(),
    }
