import json
import copy
from pathlib import Path


SOURCE = Path("healthcare_case_intelligence.serialized.json")
OUTPUT = Path("healthcare_case_intelligence.final.serialized.json")


with SOURCE.open(encoding="utf-8") as f:
    dashboard = json.load(f)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def counter_widget(
    name,
    title,
    measure,
    x,
    y,
    width=3,
    height=3,
):
    field = f"measure({measure})"

    return {
        "widget": {
            "name": name,
            "queries": [
                {
                    "name": "main_query",
                    "query": {
                        "datasetName": "case_intelligence",
                        "fields": [
                            {
                                "name": field,
                                "expression": f"MEASURE(`{measure}`)",
                            }
                        ],
                        "disaggregated": False,
                    },
                }
            ],
            "spec": {
                "version": 2,
                "frame": {
                    "title": title,
                    "showTitle": True,
                },
                "widgetType": "counter",
                "encodings": {
                    "value": {
                        "fieldName": field,
                        "rowNumber": 0,
                    }
                },
                "data": {
                    "queryName": "main_query",
                },
            },
        },
        "position": {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
        },
    }


def text_widget(name, text, x, y, width=12, height=2):
    return {
        "widget": {
            "name": name,
            "textbox": {
                "text": text
            }
        },
        "position": {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
        },
    }


def table_widget(name, title, x, y, width=12, height=7):
    fields = [
        {
            "name": "case_id",
            "expression": "`case_id`",
        },
        {
            "name": "case_type",
            "expression": "`case_type`",
        },
        {
            "name": "priority",
            "expression": "`priority`",
        },
        {
            "name": "status",
            "expression": "`status`",
        },
        {
            "name": "created_at",
            "expression": "`created_at`",
        },
    ]

    return {
        "widget": {
            "name": name,
            "queries": [
                {
                    "name": "main_query",
                    "query": {
                        "datasetName": "case_intelligence",
                        "fields": fields,
                        "disaggregated": True,
                    },
                }
            ],
            "spec": {
                "version": 2,
                "frame": {
                    "title": title,
                    "showTitle": True,
                },
                "widgetType": "table",
                "encodings": {
                    "columns": [
                        {"fieldName": "case_id"},
                        {"fieldName": "case_type"},
                        {"fieldName": "priority"},
                        {"fieldName": "status"},
                        {"fieldName": "created_at"},
                    ]
                },
                "data": {
                    "queryName": "main_query",
                },
            },
        },
        "position": {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
        },
    }


# ------------------------------------------------------------
# Page
# ------------------------------------------------------------

page = dashboard["pages"][0]

page["displayName"] = "BKK Case Intelligence"

layout = page["layout"]

# ------------------------------------------------------------
# Remove old KPI widgets so we can rebuild the top section
# ------------------------------------------------------------

remove_names = {
    "total_cases_counter",
    "open_cases_counter",
    "high_priority_counter",
    "unique_patients_counter",
}

layout[:] = [
    item
    for item in layout
    if item["widget"].get("name") not in remove_names
]


# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

layout.insert(
    0,
    text_widget(
        "bkk_header",
        "# BKK AI OPERATIONS\n"
        "### Agentic AI · Healthcare Workflow\n"
        "**● SYSTEM ONLINE**",
        0,
        0,
        12,
        3,
    ),
)


layout.insert(
    1,
    text_widget(
        "case_intelligence_header",
        "## BKK CASE INTELLIGENCE\n"
        "Agentic Workflow für Datenqualität, Prozessanalyse und Human-in-the-Loop",
        0,
        3,
        12,
        2,
    ),
)


# ------------------------------------------------------------
# KPI cards
# ------------------------------------------------------------

kpis = [
    (
        "total_cases_counter",
        "Aktive Fälle",
        "total_cases",
        0,
        5,
    ),
    (
        "open_cases_counter",
        "Open Cases",
        "open_cases",
        3,
        5,
    ),
    (
        "high_priority_counter",
        "Hohe Priorität",
        "high_priority_cases",
        6,
        5,
    ),
    (
        "unique_patients_counter",
        "Agent Pipeline",
        "unique_patients",
        9,
        5,
    ),
]

for args in kpis:
    layout.append(counter_widget(*args))


# ------------------------------------------------------------
# Analytics section
# ------------------------------------------------------------

layout.append(
    text_widget(
        "analytics_header",
        "## DATABRICKS ANALYTICS\n"
        "### Healthcare Case Analytics",
        0,
        8,
        12,
        2,
    )
)


# Existing analytics widgets are moved down
for item in layout:
    name = item["widget"].get("name")

    if name == "cases_by_type":
        item["position"] = {
            "x": 0,
            "y": 10,
            "width": 6,
            "height": 5,
        }

    elif name == "status_distribution":
        item["position"] = {
            "x": 6,
            "y": 10,
            "width": 6,
            "height": 5,
        }

    elif name == "priority_breakdown":
        item["position"] = {
            "x": 0,
            "y": 15,
            "width": 6,
            "height": 5,
        }

    elif name == "case_trends":
        item["position"] = {
            "x": 6,
            "y": 15,
            "width": 6,
            "height": 5,
        }


# ------------------------------------------------------------
# Case Management
# ------------------------------------------------------------

layout.append(
    text_widget(
        "case_management_header",
        "## CASE MANAGEMENT\n"
        "### Healthcare Cases",
        0,
        20,
        12,
        2,
    )
)


layout.append(
    table_widget(
        "healthcare_cases",
        "Healthcare Cases",
        0,
        22,
        12,
        7,
    )
)


# ------------------------------------------------------------
# AI Case Intelligence
# ------------------------------------------------------------

layout.append(
    text_widget(
        "ai_case_intelligence",
        "## AI CASE INTELLIGENCE\n\n"
        "**Select a case**\n\n"
        "Wähle einen Fall aus der linken Liste, "
        "um den vollständigen Agentic-AI-Workflow auszuführen.\n\n"
        "✓ Data Quality    "
        "✓ Process Analysis    "
        "✓ Medical AI    "
        "✓ RAG    "
        "✓ Human Review",
        0,
        29,
        12,
        5,
    )
)


# ------------------------------------------------------------
# Agentic Architecture
# ------------------------------------------------------------

layout.append(
    text_widget(
        "agentic_ai_architecture",
        "## AGENTIC AI ARCHITECTURE\n\n"
        "**Kontrollierter autonomer Workflow**\n\n"
        "**01 Data Quality** → "
        "**02 Process Agent** → "
        "**03 Medical Agent** → "
        "**04 Triage Agent** → "
        "**05 Governance Agent** → "
        "**06 Human Review**",
        0,
        34,
        12,
        5,
    )
)


# ------------------------------------------------------------
# UI
# ------------------------------------------------------------

dashboard["uiSettings"] = {
    "theme": {
        "widgetHeaderAlignment": "ALIGNMENT_UNSPECIFIED"
    },
    "applyModeEnabled": False,
}


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

with OUTPUT.open("w", encoding="utf-8") as f:
    json.dump(
        dashboard,
        f,
        indent=2,
        ensure_ascii=False,
    )


print(f"Created: {OUTPUT}")
