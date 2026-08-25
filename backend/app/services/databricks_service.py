from typing import Any

from app.tools.databricks_tool import execute_databricks_sql


class DatabricksService:

    def query(self, sql: str) -> dict[str, Any]:
        return execute_databricks_sql(sql)


databricks_service = DatabricksService()
