import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

MODEL = "llama3.2:1b"
ENDPOINT = os.getenv("OLLAMA_URL", "http://localhost:11434")
MINIMUM_SCORE = 0.80

with open(ROOT / "mlops" / "model.yaml", encoding="utf-8") as f:
    model_config = f.read()

with open(ROOT / "mlops" / "evaluation" / "cases.json", encoding="utf-8") as f:
    cases = json.load(f)

passed = 0
results = []

for case in cases:
    payload = json.dumps({
        "model": MODEL,
        "prompt": case["prompt"],
        "stream": False,
        "format": "json"
    }).encode()

    request = urllib.request.Request(
        f"{ENDPOINT}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode())

        raw_output = result.get("response", "")
        output = json.loads(raw_output)

        if (
            isinstance(output, dict)
            and output.get("risk") == case["expected_risk"]
            and isinstance(output.get("reason"), str)
            and output["reason"].strip()
        ):
            print(f"[PASS] {case['id']}")
            results.append({
                "id": case["id"],
                "status": "PASS",
                "expected_risk": case["expected_risk"],
                "output": output,
            })
            passed += 1
        else:
            print(f"[FAIL] {case['id']}")
            print(f"       output: {raw_output[:500]}")
            results.append({
                "id": case["id"],
                "status": "FAIL",
                "expected_risk": case["expected_risk"],
                "output": raw_output[:500],
            })

    except Exception as exc:
        print(f"[FAIL] {case['id']}: {exc}")
        results.append({
            "id": case["id"],
            "status": "FAIL",
            "expected_risk": case["expected_risk"],
            "error": str(exc),
        })

score = passed / len(cases)

print()
print(f"Model: {MODEL}")
print(f"Passed: {passed}/{len(cases)}")
print(f"Score: {score:.2%}")

Path("mlops-evaluation-result.json").write_text(
    json.dumps({
        "model": MODEL,
        "passed": passed,
        "total": len(cases),
        "score": score,
        "minimum_score": MINIMUM_SCORE,
        "results": results,
    }, indent=2),
    encoding="utf-8",
)

if score < MINIMUM_SCORE:
    print(f"MLOps quality gate FAILED (minimum {MINIMUM_SCORE:.0%})")
    sys.exit(1)

print(f"MLOps quality gate PASSED (minimum {MINIMUM_SCORE:.0%})")
