import csv
import os
from pathlib import Path

from sqlalchemy import create_engine, text


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://healthcare:healthcare@localhost:5433/healthcare_ai",
)

OUTPUT_DIR = Path("databricks_export")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "cases.csv"

engine = create_engine(DATABASE_URL)

query = text("""
    SELECT
        id,
        patient_id,
        case_type,
        status,
        priority,
        description,
        created_at
    FROM cases
    ORDER BY id
""")

with engine.connect() as conn:
    rows = conn.execute(query).mappings().all()

with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "id",
            "patient_id",
            "case_type",
            "status",
            "priority",
            "description",
            "created_at",
        ],
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"Exported {len(rows)} cases to {OUTPUT_FILE}")
