import json

OUTPUT = "healthcare_case_intelligence.v2.serialized.json"

dashboard = {
    "datasets": [
        {
            "name": "summary",
            "displayName": "Case Summary",
            "queryLines": [
                "SELECT total_cases, open_cases, high_priority_cases, closed_cases, total_categories, sick_pay_cases",
                "FROM workspace.gold.case_summary"
            ]
        },
        {
            "name": "case_analytics",
            "displayName": "Healthcare Case Analytics",
            "queryLines": [
                "SELECT",
                "  case_type,",
                "  total_cases,",
                "  open_cases,",
                "  high_priority_cases,",
                "  closed_cases",
                "FROM workspace.gold.case_analytics",
                "ORDER BY total_cases DESC, case_type"
            ]
        },
        {
            "name": "status_analytics",
            "displayName": "Case Status",
            "queryLines": [
                "SELECT 'Open' AS status, SUM(open_cases) AS cases",
                "FROM workspace.gold.case_analytics",
                "UNION ALL",
                "SELECT 'High Priority' AS status, SUM(high_priority_cases) AS cases",
                "FROM workspace.gold.case_analytics",
                "UNION ALL",
                "SELECT 'Closed' AS status, SUM(closed_cases) AS cases",
                "FROM workspace.gold.case_analytics"
            ]
        },
        {
            "name": "sick_pay",
            "displayName": "Sick Pay Analytics",
            "queryLines": [
                "SELECT",
                "  case_type,",
                "  total_cases,",
                "  open_cases,",
                "  high_priority_cases",
                "FROM workspace.gold.sick_pay_analytics",
                "ORDER BY total_cases DESC, case_type"
            ]
        }
    ],

    "pages": [
        {
            "name": "bkk_case_intelligence",
            "displayName": "BKK Case Intelligence",
            "layout": [

                # -------------------------------------------------
                # KPI 1
                # -------------------------------------------------
                {
                    "widget": {
                        "name": "total_cases",
                        "queries": [
                            {
                                "name": "main_query",
                                "query": {
                                    "datasetName": "summary",
                                    "fields": [
                                        {
                                            "name": "total_cases",
                                            "expression": "`total_cases`"
                                        }
                                    ],
                                    "disaggregated": False
                                }
                            }
                        ],
                        "spec": {
                            "version": 2,
                            "frame": {
                                "title": "Aktive Fälle",
                                "showTitle": True
                            },
                            "widgetType": "counter",
                            "encodings": {
                                "value": {
                                    "fieldName": "total_cases",
                                    "rowNumber": 0
                                }
                            },
                            "data": {
                                "queryName": "main_query"
                            }
                        }
                    },
                    "position": {
                        "x": 0,
                        "y": 0,
                        "width": 3,
                        "height": 3
                    }
                },

                # -------------------------------------------------
                # KPI 2
                # -------------------------------------------------
                {
                    "widget": {
                        "name": "open_cases",
                        "queries": [
                            {
                                "name": "main_query",
                                "query": {
                                    "datasetName": "summary",
                                    "fields": [
                                        {
                                            "name": "open_cases",
                                            "expression": "`open_cases`"
                                        }
                                    ],
                                    "disaggregated": False
                                }
                            }
                        ],
                        "spec": {
                            "version": 2,
                            "frame": {
                                "title": "Offene Fälle",
                                "showTitle": True
                            },
                            "widgetType": "counter",
                            "encodings": {
                                "value": {
                                    "fieldName": "open_cases",
                                    "rowNumber": 0
                                }
                            },
                            "data": {
                                "queryName": "main_query"
                            }
                        }
                    },
                    "position": {
                        "x": 3,
                        "y": 0,
                        "width": 3,
                        "height": 3
                    }
                },

                # -------------------------------------------------
                # KPI 3
                # -------------------------------------------------
                {
                    "widget": {
                        "name": "high_priority_cases",
                        "queries": [
                            {
                                "name": "main_query",
                                "query": {
                                    "datasetName": "summary",
                                    "fields": [
                                        {
                                            "name": "high_priority_cases",
                                            "expression": "`high_priority_cases`"
                                        }
                                    ],
                                    "disaggregated": False
                                }
                            }
                        ],
                        "spec": {
                            "version": 2,
                            "frame": {
                                "title": "Hohe Priorität",
                                "showTitle": True
                            },
                            "widgetType": "counter",
                            "encodings": {
                                "value": {
                                    "fieldName": "high_priority_cases",
                                    "rowNumber": 0
                                }
                            },
                            "data": {
                                "queryName": "main_query"
                            }
                        }
                    },
                    "position": {
                        "x": 6,
                        "y": 0,
                        "width": 3,
                        "height": 3
                    }
                },

                # -------------------------------------------------
                # KPI 4
                # -------------------------------------------------
                {
                    "widget": {
                        "name": "total_categories",
                        "queries": [
                            {
                                "name": "main_query",
                                "query": {
                                    "datasetName": "summary",
                                    "fields": [
                                        {
                                            "name": "total_categories",
                                            "expression": "`total_categories`"
                                        }
                                    ],
                                    "disaggregated": False
                                }
                            }
                        ],
                        "spec": {
                            "version": 2,
                            "frame": {
                                "title": "Kategorien",
                                "showTitle": True
                            },
                            "widgetType": "counter",
                            "encodings": {
                                "value": {
                                    "fieldName": "total_categories",
                                    "rowNumber": 0
                                }
                            },
                            "data": {
                                "queryName": "main_query"
                            }
                        }
                    },
                    "position": {
                        "x": 9,
                        "y": 0,
                        "width": 3,
                        "height": 3
                    }
                },

                # -------------------------------------------------
                # CASES BY TYPE
                # -------------------------------------------------
                {
                    "widget": {
                        "name": "cases_by_type",
                        "queries": [
                            {
                                "name": "main_query",
                                "query": {
                                    "datasetName": "case_analytics",
                                    "fields": [
                                        {
                                            "name": "case_type",
                                            "expression": "`case_type`"
                                        },
                                        {
                                            "name": "total_cases",
                                            "expression": "`total_cases`"
                                        }
                                    ],
                                    "disaggregated": True
                                }
                            }
                        ],
                        "spec": {
                            "version": 3,
                            "frame": {
                                "title": "Healthcare Case Analytics",
                                "showTitle": True
                            },
                            "widgetType": "bar",
                            "encodings": {
                                "x": {
                                    "fieldName": "case_type",
                                    "displayName": "Kategorie",
                                    "scale": {
                                        "type": "categorical"
                                    }
                                },
                                "y": {
                                    "fieldName": "total_cases",
                                    "displayName": "Fälle",
                                    "scale": {
                                        "type": "quantitative"
                                    }
                                }
                            },
                            "data": {
                                "queryName": "main_query"
                            }
                        }
                    },
                    "position": {
                        "x": 0,
                        "y": 4,
                        "width": 6,
                        "height": 5
                    }
                },

                # -------------------------------------------------
                # STATUS
                # -------------------------------------------------
                {
                    "widget": {
                        "name": "status_distribution",
                        "queries": [
                            {
                                "name": "main_query",
                                "query": {
                                    "datasetName": "status_analytics",
                                    "fields": [
                                        {
                                            "name": "status",
                                            "expression": "`status`"
                                        },
                                        {
                                            "name": "cases",
                                            "expression": "`cases`"
                                        }
                                    ],
                                    "disaggregated": True
                                }
                            }
                        ],
                        "spec": {
                            "version": 3,
                            "frame": {
                                "title": "Case Status Distribution",
                                "showTitle": True
                            },
                            "widgetType": "pie",
                            "encodings": {
                                "angle": {
                                    "fieldName": "cases",
                                    "displayName": "Fälle",
                                    "scale": {
                                        "type": "quantitative"
                                    }
                                },
                                "color": {
                                    "fieldName": "status",
                                    "displayName": "Status",
                                    "scale": {
                                        "type": "categorical"
                                    }
                                }
                            },
                            "data": {
                                "queryName": "main_query"
                            }
                        }
                    },
                    "position": {
                        "x": 6,
                        "y": 4,
                        "width": 6,
                        "height": 5
                    }
                },

                # -------------------------------------------------
                # OPEN / HIGH / CLOSED TABLE
                # -------------------------------------------------
                {
                    "widget": {
                        "name": "case_analytics_table",
                        "queries": [
                            {
                                "name": "main_query",
                                "query": {
                                    "datasetName": "case_analytics",
                                    "fields": [
                                        {
                                            "name": "case_type",
                                            "expression": "`case_type`"
                                        },
                                        {
                                            "name": "total_cases",
                                            "expression": "`total_cases`"
                                        },
                                        {
                                            "name": "open_cases",
                                            "expression": "`open_cases`"
                                        },
                                        {
                                            "name": "high_priority_cases",
                                            "expression": "`high_priority_cases`"
                                        },
                                        {
                                            "name": "closed_cases",
                                            "expression": "`closed_cases`"
                                        }
                                    ],
                                    "disaggregated": True
                                }
                            }
                        ],
                        "spec": {
                            "version": 2,
                            "frame": {
                                "title": "Healthcare Case Overview",
                                "showTitle": True
                            },
                            "widgetType": "table",
                            "encodings": {
                                "columns": [
                                    {
                                        "fieldName": "case_type"
                                    },
                                    {
                                        "fieldName": "total_cases"
                                    },
                                    {
                                        "fieldName": "open_cases"
                                    },
                                    {
                                        "fieldName": "high_priority_cases"
                                    },
                                    {
                                        "fieldName": "closed_cases"
                                    }
                                ]
                            },
                            "data": {
                                "queryName": "main_query"
                            }
                        }
                    },
                    "position": {
                        "x": 0,
                        "y": 9,
                        "width": 12,
                        "height": 6
                    }
                },

                # -------------------------------------------------
                # SICK PAY
                # -------------------------------------------------
                {
                    "widget": {
                        "name": "sick_pay_cases",
                        "queries": [
                            {
                                "name": "main_query",
                                "query": {
                                    "datasetName": "sick_pay",
                                    "fields": [
                                        {
                                            "name": "case_type",
                                            "expression": "`case_type`"
                                        },
                                        {
                                            "name": "total_cases",
                                            "expression": "`total_cases`"
                                        },
                                        {
                                            "name": "open_cases",
                                            "expression": "`open_cases`"
                                        },
                                        {
                                            "name": "high_priority_cases",
                                            "expression": "`high_priority_cases`"
                                        }
                                    ],
                                    "disaggregated": True
                                }
                            }
                        ],
                        "spec": {
                            "version": 2,
                            "frame": {
                                "title": "Sick Pay Analytics",
                                "showTitle": True
                            },
                            "widgetType": "table",
                            "encodings": {
                                "columns": [
                                    {
                                        "fieldName": "case_type"
                                    },
                                    {
                                        "fieldName": "total_cases"
                                    },
                                    {
                                        "fieldName": "open_cases"
                                    },
                                    {
                                        "fieldName": "high_priority_cases"
                                    }
                                ]
                            },
                            "data": {
                                "queryName": "main_query"
                            }
                        }
                    },
                    "position": {
                        "x": 0,
                        "y": 16,
                        "width": 8,
                        "height": 5
                    }
                },

                # -------------------------------------------------
                # SICK PAY KPI
                # -------------------------------------------------
                {
                    "widget": {
                        "name": "sick_pay_counter",
                        "queries": [
                            {
                                "name": "main_query",
                                "query": {
                                    "datasetName": "summary",
                                    "fields": [
                                        {
                                            "name": "sick_pay_cases",
                                            "expression": "`sick_pay_cases`"
                                        }
                                    ],
                                    "disaggregated": False
                                }
                            }
                        ],
                        "spec": {
                            "version": 2,
                            "frame": {
                                "title": "Sick Pay Fälle",
                                "showTitle": True
                            },
                            "widgetType": "counter",
                            "encodings": {
                                "value": {
                                    "fieldName": "sick_pay_cases",
                                    "rowNumber": 0
                                }
                            },
                            "data": {
                                "queryName": "main_query"
                            }
                        }
                    },
                    "position": {
                        "x": 8,
                        "y": 16,
                        "width": 4,
                        "height": 5
                    }
                }
            ],
            "pageType": "PAGE_TYPE_CANVAS",
            "layoutVersion": "GRID_V1"
        }
    ],

    "uiSettings": {
        "theme": {
            "widgetHeaderAlignment": "ALIGNMENT_UNSPECIFIED"
        },
        "applyModeEnabled": False
    }
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(dashboard, f, indent=2, ensure_ascii=False)

print(f"Created: {OUTPUT}")
