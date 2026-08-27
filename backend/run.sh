#!/usr/bin/env bash
set -euo pipefail

export DATABASE_URL="${DATABASE_URL:-postgresql+psycopg://banking:banking@localhost:5432/banking_poc}"
python3 seed.py
python3 -m uvicorn app.main:app --reload --port 8000
