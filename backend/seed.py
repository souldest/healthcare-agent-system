import os
import random

from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://banking:banking@localhost:5432/banking_poc",
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
random.seed(42)

COUNTRIES = ["Germany", "France", "Italy", "Spain", "Netherlands", "Austria"]
PRODUCTS = ["Mortgage", "Consumer Loan", "Corporate Loan", "Credit Card"]
NAMES = [
    "Alpha GmbH", "Bergmann AG", "Delta Retail", "Epsilon SE", "Fischer KG",
    "Giga Solutions", "Hansa Trading", "Iris Finance", "Juno Tech", "Kappa Logistics",
]


def main() -> None:
    with engine.begin() as conn:
        conn.exec_driver_sql("DROP TABLE IF EXISTS data_quality_checks")
        conn.exec_driver_sql("DROP TABLE IF EXISTS customer_risk")
        conn.exec_driver_sql("""
            CREATE TABLE customer_risk (
                customer_id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                country TEXT NOT NULL,
                product TEXT NOT NULL,
                credit_exposure NUMERIC(18,2) NOT NULL,
                income NUMERIC(18,2) NOT NULL,
                risk_score NUMERIC(5,1) NOT NULL,
                risk_category TEXT NOT NULL,
                default_flag BOOLEAN NOT NULL,
                transaction_count_90d INTEGER NOT NULL,
                unusual_transaction_flag BOOLEAN NOT NULL,
                risk_reason TEXT NOT NULL
            )
        """)
        conn.exec_driver_sql("""
            CREATE TABLE data_quality_checks (
                check_name TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                issue_count INTEGER NOT NULL,
                severity INTEGER NOT NULL,
                details TEXT NOT NULL
            )
        """)

        for i in range(1, 501):
            country = random.choice(COUNTRIES)
            product = random.choice(PRODUCTS)
            income = round(random.uniform(28000, 220000), 2)
            exposure = round(random.uniform(5000, 1200000), 2)
            tx = random.randint(2, 480)
            unusual = random.random() < 0.07
            base = random.uniform(5, 72)
            risk_score = min(99, round(base + (18 if unusual else 0) + (10 if exposure > 800000 else 0), 1))
            default = (risk_score >= 80 and random.random() < 0.34) or random.random() < 0.02
            if risk_score >= 70:
                category = "High"
                reasons = ["Elevated risk score", "High exposure", "Unusual transaction pattern"]
            elif risk_score >= 40:
                category = "Medium"
                reasons = ["Moderate risk score", "Exposure requires monitoring"]
            else:
                category = "Low"
                reasons = ["Low modeled risk"]
            if default:
                reasons.append("Observed default flag")
            reason = "; ".join(reasons[:2] + ([reasons[-1]] if default else []))

            if i in (73, 181):
                tx = -3  # deliberate DQ defects for the demo

            conn.execute(text("""
                INSERT INTO customer_risk
                (customer_id, customer_name, country, product, credit_exposure, income, risk_score,
                 risk_category, default_flag, transaction_count_90d, unusual_transaction_flag, risk_reason)
                VALUES (:customer_id, :customer_name, :country, :product, :credit_exposure, :income, :risk_score,
                        :risk_category, :default_flag, :transaction_count_90d, :unusual_transaction_flag, :risk_reason)
            """), {
                "customer_id": f"C{i:05d}",
                "customer_name": random.choice(NAMES),
                "country": country,
                "product": product,
                "credit_exposure": exposure,
                "income": income,
                "risk_score": risk_score,
                "risk_category": category,
                "default_flag": default,
                "transaction_count_90d": tx,
                "unusual_transaction_flag": unusual,
                "risk_reason": reason,
            })

        checks = [
            ("Null customer IDs", "PASS", 0, 5, "Primary key is complete."),
            ("Negative transaction counts", "FAIL", 2, 4, "Two records contain an invalid negative transaction count."),
            ("Missing country", "PASS", 0, 3, "Country is populated for all records."),
            ("Exposure <= 0", "PASS", 0, 4, "No non-positive exposure values detected."),
            ("Duplicate customer IDs", "PASS", 0, 5, "Customer IDs are unique."),
        ]
        for check in checks:
            conn.execute(text("""
                INSERT INTO data_quality_checks(check_name, status, issue_count, severity, details)
                VALUES (:check_name, :status, :issue_count, :severity, :details)
            """), dict(zip(["check_name", "status", "issue_count", "severity", "details"], check)))

    print("Seeded PostgreSQL database")


if __name__ == "__main__":
    main()
