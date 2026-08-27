# 5-Minuten-Demo im Vorstellungsgespräch

## 1. Problem (30 Sek.)
„Ich habe einen vereinfachten Banking-Use-Case gewählt, weil Risk und Regulatory Reporting direkt in der Position genannt werden. Ziel ist zu zeigen, wie aus Rohdaten eine fachlich nutzbare Analytics-Lösung wird.“

## 2. Architektur (60 Sek.)
„Die Daten landen zunächst in einer SQL-Schicht. Darauf laufen Data-Quality-Checks und Risk-Analysen. FastAPI stellt die Ergebnisse als REST APIs bereit und ein React-Dashboard konsumiert sie.“

Danach die Erweiterung nennen:
„In einer produktiven Cloud-Architektur würde ich diese Verarbeitung auf eine Lakehouse-Plattform wie Databricks heben, z. B. Bronze/Silver/Gold.“

## 3. Data Quality (60 Sek.)
Zum Data-Quality-Block wechseln.

Sagen:
„Ich habe absichtlich zwei fehlerhafte Transaktionszählungen eingebaut. Dadurch kann ich zeigen, dass Data Quality nicht nur ein nachträglicher Report ist, sondern ein Teil des Analytics-Prozesses.“

## 4. Risk Analytics (90 Sek.)
Risk Distribution, Länder und High-Risk-Fälle zeigen.

Erklären:
- Exposure
- Risk Score
- Default Rate
- High-Risk Exposure

„Die konkrete Formel ist hier bewusst demonstrativ und nicht als echtes Kreditrisikomodell gedacht.“

## 5. Consulting-Perspektive (60 Sek.)
„Bei einem echten Kundenprojekt würde ich als Nächstes die fachliche KPI-Definition, Datenherkunft, Berechtigungen, Historisierung, Data Lineage, regulatorische Anforderungen und Betriebsprozesse klären.“

## Gute Abschlussfrage an msg for banking
„Welche Data-Analytics- oder BI-Plattform spielt in Ihren aktuellen Risk- und Regulatory-Projekten die größte Rolle – eher Databricks, Snowflake oder bestehende Bankplattformen?“
