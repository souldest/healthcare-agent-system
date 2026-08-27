# Bank Risk & Regulatory Analytics POC – msg for banking

Ein kleines End-to-End-Demoprojekt als Vorbereitung auf ein Data-Analytics-&-BI-Consulting-Gespräch bei msg for banking.

## Ziel

Der POC demonstriert einen vereinfachten Analytics Lifecycle:

**synthetische Bankdaten → Data-Quality-Checks → Risk-KPIs → FastAPI → React-Dashboard**

Die Daten sind vollständig synthetisch. Der POC stellt **keine echte regulatorische Meldung** dar.

## Technologie

- Python 3.11+
- FastAPI / Uvicorn
- **PostgreSQL**
- SQLAlchemy + psycopg
- SQL
- React + Vite
- HTML/CSS
- Linux/WSL/Bash-tauglich

## PostgreSQL-Konfiguration

Standardmäßig verwendet das Projekt:

```text
postgresql+psycopg://banking:banking@localhost:5432/banking_poc
```

Die URL kann über `DATABASE_URL` überschrieben werden.

Beispiel:

```bash
export DATABASE_URL="postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE"
```

## Starten mit Docker Compose

Im Projektverzeichnis:

```bash
docker compose up
```

Danach:

- API: http://localhost:8000/docs
- Frontend: http://localhost:5173
- PostgreSQL: localhost:5432

## Backend lokal starten

Voraussetzung: PostgreSQL läuft und die Datenbank `banking_poc` existiert.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql+psycopg://banking:banking@localhost:5432/banking_poc"
python seed.py
uvicorn app.main:app --reload --port 8000
```

API: http://localhost:8000/docs

## Frontend

In einem zweiten Terminal:

```bash
cd frontend
npm install
npm run dev
```

Dann die von Vite angezeigte URL öffnen (typischerweise http://localhost:5173).

## API-Endpunkte

- `GET /api/health`
- `GET /api/risk/overview`
- `GET /api/risk/by-country`
- `GET /api/risk/high-risk?limit=20`
- `GET /api/data-quality`
- `GET /api/reporting/summary`
- `GET /api/customers/{customer_id}`

## Architektur

```text
Banking Sources
      ↓
  Data Ingestion
      ↓
 PostgreSQL / SQL
      ↓
 Data Quality + Risk Analytics
      ↓
    FastAPI
      ↓
 React Dashboard
```

Für eine Cloud-/Lakehouse-Zielarchitektur lässt sich PostgreSQL als operative/POC-Datenbank durch eine Plattform wie Databricks/Snowflake ergänzen oder ablösen. Die Business-Logik und APIs bleiben dabei konzeptionell getrennt.

## Interview-Erklärung in 60 Sekunden

> „Ich habe einen kleinen Banking-Analytics-POC entwickelt, um den Analytics Lifecycle praktisch abzubilden. Ich verwende synthetische Kunden- und Exposure-Daten in PostgreSQL, prüfe die Datenqualität, berechne Risk-KPIs und stelle sie über eine FastAPI bereit. Ein React-Dashboard konsumiert diese APIs und macht die Ergebnisse für Fachanwender sichtbar. Für eine produktive Cloud-Architektur würde ich die Datenverarbeitung beispielsweise auf eine Lakehouse-Plattform wie Databricks erweitern. Mir war wichtig, nicht nur ein Dashboard zu bauen, sondern Datenqualität, Analytics, API und Consumer in einer durchgängigen Lösung zu verbinden.“
