from typing import Any

from backend.app.tools.databricks_tool import (
    execute_databricks_sql,
    get_case_analytics,
    get_case_summary,
    get_sick_pay_analytics,
)


class DatabricksService:

    def query(self, sql: str) -> dict[str, Any]:
        return execute_databricks_sql(sql)

    def get_case_analytics(self) -> list[dict[str, Any]]:
        return get_case_analytics()

    def get_sick_pay_analytics(self) -> list[dict[str, Any]]:
        return get_sick_pay_analytics()

    def get_case_summary(self) -> dict[str, Any]:
        return get_case_summary()


databricks_service = DatabricksService()
