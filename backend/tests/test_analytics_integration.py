import requests


BASE_URL = "http://localhost:8002"


def get_json(path: str):
    response = requests.get(
        f"{BASE_URL}{path}",
        timeout=30,
    )

    assert response.status_code == 200, (
        f"{path} returned HTTP {response.status_code}: "
        f"{response.text}"
    )

    return response.json()


def test_analytics_end_to_end():
    # ---------------------------------------------------------
    # 1. Case Summary
    # ---------------------------------------------------------
    summary = get_json("/api/analytics/summary")

    assert isinstance(summary, dict)

    required_summary_fields = {
        "total_cases",
        "open_cases",
        "high_priority_cases",
        "closed_cases",
        "total_categories",
        "sick_pay_cases",
    }

    assert required_summary_fields.issubset(summary.keys())

    assert isinstance(summary["total_cases"], int)
    assert isinstance(summary["open_cases"], int)
    assert isinstance(summary["high_priority_cases"], int)
    assert isinstance(summary["closed_cases"], int)
    assert isinstance(summary["total_categories"], int)
    assert isinstance(summary["sick_pay_cases"], int)

    # ---------------------------------------------------------
    # 2. Case Analytics
    # ---------------------------------------------------------
    case_analytics = get_json("/api/analytics/cases")

    assert isinstance(case_analytics, list)
    assert len(case_analytics) == summary["total_categories"]

    required_case_fields = {
        "case_type",
        "total_cases",
        "open_cases",
        "high_priority_cases",
        "closed_cases",
    }

    for item in case_analytics:
        assert required_case_fields.issubset(item.keys())

        assert isinstance(item["case_type"], str)
        assert isinstance(item["total_cases"], int)
        assert isinstance(item["open_cases"], int)
        assert isinstance(item["high_priority_cases"], int)
        assert isinstance(item["closed_cases"], int)

    # ---------------------------------------------------------
    # 3. Konsistenz: Case Analytics -> Summary
    # ---------------------------------------------------------
    total_cases = sum(
        item["total_cases"]
        for item in case_analytics
    )

    open_cases = sum(
        item["open_cases"]
        for item in case_analytics
    )

    high_priority_cases = sum(
        item["high_priority_cases"]
        for item in case_analytics
    )

    closed_cases = sum(
        item["closed_cases"]
        for item in case_analytics
    )

    assert total_cases == summary["total_cases"]
    assert open_cases == summary["open_cases"]
    assert high_priority_cases == summary["high_priority_cases"]
    assert closed_cases == summary["closed_cases"]

    # ---------------------------------------------------------
    # 4. Sick Pay Analytics
    # ---------------------------------------------------------
    sick_pay = get_json("/api/analytics/sick-pay")

    assert isinstance(sick_pay, list)
    assert len(sick_pay) >= 1

    sick_pay_total = sum(
        item["total_cases"]
        for item in sick_pay
    )

    assert sick_pay_total == summary["sick_pay_cases"]

    # ---------------------------------------------------------
    # 5. Demo-Datensatz: konkrete Erwartungen
    # ---------------------------------------------------------
    # Diese Werte entsprechen dem aktuellen PoC-Datensatz.
    assert summary["total_cases"] == 4
    assert summary["open_cases"] == 4
    assert summary["high_priority_cases"] == 2
    assert summary["closed_cases"] == 0
    assert summary["total_categories"] == 3
    assert summary["sick_pay_cases"] == 1

    # ---------------------------------------------------------
    # 6. Case-Type-Werte prüfen
    # ---------------------------------------------------------
    by_type = {
        item["case_type"]: item
        for item in case_analytics
    }

    assert by_type["CARDIOLOGY"]["total_cases"] == 2
    assert by_type["CARDIOLOGY"]["open_cases"] == 2
    assert by_type["CARDIOLOGY"]["high_priority_cases"] == 2
    assert by_type["CARDIOLOGY"]["closed_cases"] == 0

    assert by_type["GENERAL"]["total_cases"] == 1
    assert by_type["GENERAL"]["open_cases"] == 1
    assert by_type["GENERAL"]["high_priority_cases"] == 0
    assert by_type["GENERAL"]["closed_cases"] == 0

    assert by_type["SICK_PAY"]["total_cases"] == 1
    assert by_type["SICK_PAY"]["open_cases"] == 1
    assert by_type["SICK_PAY"]["high_priority_cases"] == 0
    assert by_type["SICK_PAY"]["closed_cases"] == 0

    # ---------------------------------------------------------
    # 7. Sick-Pay-Datensatz prüfen
    # ---------------------------------------------------------
    sick_pay_item = sick_pay[0]

    assert sick_pay_item["case_type"] == "SICK_PAY"
    assert sick_pay_item["total_cases"] == 1
    assert sick_pay_item["open_cases"] == 1
    assert sick_pay_item["high_priority_cases"] == 0
