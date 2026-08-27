# Architektur

```text
              Synthetische Banking-Daten
                         |
                         v
                 SQLite / SQL Layer
                         |
              +----------+----------+
              |                     |
              v                     v
       Data Quality Checks      Risk Analytics
              |                     |
              +----------+----------+
                         |
                         v
                     FastAPI
                         |
                         v
                    React UI
                         |
                         v
                 Fachanwender / BI
```

## Erweiterung auf Databricks / Lakehouse

Die SQLite-Schicht kann bei einer produktiveren Architektur durch eine Cloud-/Lakehouse-Plattform ersetzt werden:

```text
Sources -> Bronze -> Silver -> Gold -> BI / APIs
             |         |        |
             |         |        +-- Risk KPIs
             |         +----------- Quality / standardized data
             +--------------------- Raw / immutable data
```

Mögliche Ergänzungen: Azure Data Factory / Databricks Jobs für Ingestion, Delta Lake für Tabellen, Unity Catalog für Governance, Power BI für fachliches Reporting und Monitoring über Cloud-/Platform-Services.
