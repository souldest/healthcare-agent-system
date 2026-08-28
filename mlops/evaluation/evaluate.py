import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

MODEL = "llama3.2:1b"
ENDPOINT = os.getenv("OLLAMA_URL", "http://localhost:11434")

with open(ROOT / "mlops" / "model.yaml", encoding="utf-8") as f:
    model_config = f.read()

with open(ROOT / "mlops" / "evaluation" / "cases.json", encoding="utf-8") as f:
    cases = json.load(f)

passed = 0

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
            passed += 1
        else:
            print(f"[FAIL] {case['id']}")
            print(f"       output: {raw_output[:500]}")

    except Exception as exc:
        print(f"[FAIL] {case['id']}: {exc}")

score = passed / len(cases)

print()
print(f"Model: {MODEL}")
print(f"Passed: {passed}/{len(cases)}")
print(f"Score: {score:.2%}")

minimum_score = 0.80

if score < minimum_score:
    print(f"MLOps quality gate FAILED (minimum {minimum_score:.0%})")
    sys.exit(1)

print(f"MLOps quality gate PASSED (minimum {minimum_score:.0%})")
