"""Phase G — Regression test runner.

Compares new OSRM routes (self-hosted) against the captured public demo baseline.
Flags any pair where:
  - New route is MORE THAN 50% longer than baseline (regression)
  - New route FAILED but baseline succeeded (routing hole)
  - Far-outside pair result changed by more than 5% (scope leak)

Usage:
    python routing/scripts/run_regression_tests.py [--osrm-url URL]
    python routing/scripts/run_regression_tests.py --osrm-url http://localhost:5001

Reads data/routing/baseline/public_demo.json as the baseline.
"""

import json
import time
import urllib.request
import urllib.error
from pathlib import Path

BASELINE_PATH = Path("data/routing/baseline/public_demo.json")
REGRESSION_THRESHOLD_PCT = 50.0   # alert if new route > baseline * (1 + threshold/100)
SCOPE_LEAK_THRESHOLD_PCT  = 5.0   # far-outside pairs must not change by more than this
REQUEST_DELAY_S = 0.5


def fetch_route(osrm_url: str, origin: dict, dest: dict) -> dict:
    url = (
        f"{osrm_url}/route/v1/foot/"
        f"{origin['lon']},{origin['lat']};{dest['lon']},{dest['lat']}"
        "?overview=false&geometries=geojson&steps=false"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "geoai-regression/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read())
            if body.get("code") == "Ok" and body.get("routes"):
                r = body["routes"][0]
                return {"code": "Ok", "distance_m": r["distance"], "duration_s": r["duration"]}
            return {"code": body.get("code", "UNKNOWN"), "distance_m": None, "duration_s": None}
    except Exception as e:
        return {"code": "ERROR", "distance_m": None, "duration_s": None, "error": str(e)}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--osrm-url", default="http://localhost:5001")
    args = parser.parse_args()

    if not BASELINE_PATH.exists():
        print(f"ERROR: Baseline not found at {BASELINE_PATH}")
        print("       Run routing/scripts/capture_baseline.py first.")
        return

    baseline = json.loads(BASELINE_PATH.read_text())
    baseline_pairs = baseline["pairs"]
    print(f"=== Regression Test — Phase G ===")
    print(f"Baseline: {BASELINE_PATH} ({len(baseline_pairs)} pairs, captured {baseline['captured_at'][:10]})")
    print(f"Testing:  {args.osrm_url}")
    print()

    results = []
    n_pass = n_regression = n_fail = n_scope_leak = 0

    for i, bp in enumerate(baseline_pairs):
        kind   = bp["kind"]
        origin = bp["origin"]
        dest   = bp["dest"]
        b_dist = bp.get("distance_m")
        b_code = bp.get("code")

        print(f"[{i+1}/{len(baseline_pairs)}] {kind}: {origin['name']} -> {dest['name']}", end=" ... ", flush=True)

        new = fetch_route(args.osrm_url, origin, dest)
        n_dist = new.get("distance_m")
        n_code = new.get("code")

        status = "PASS"
        notes = []

        if b_code == "Ok" and n_code != "Ok":
            status = "FAIL"
            n_fail += 1
            notes.append(f"Routing HOLE (baseline Ok, new code={n_code})")
        elif b_code == "Ok" and n_code == "Ok":
            if b_dist and n_dist:
                change_pct = (n_dist - b_dist) / b_dist * 100
                threshold = SCOPE_LEAK_THRESHOLD_PCT if kind == "far_outside" else REGRESSION_THRESHOLD_PCT
                if change_pct > threshold:
                    if kind == "far_outside":
                        status = "SCOPE_LEAK"
                        n_scope_leak += 1
                    else:
                        status = "REGRESSION"
                        n_regression += 1
                    notes.append(f"dist {b_dist:.0f}m -> {n_dist:.0f}m ({change_pct:+.1f}%)")
                elif change_pct < -10:
                    # Improvement
                    notes.append(f"IMPROVED {b_dist:.0f}m -> {n_dist:.0f}m ({change_pct:+.1f}%)")
                else:
                    notes.append(f"{b_dist:.0f}m -> {n_dist:.0f}m ({change_pct:+.1f}%)")

        if status == "PASS":
            n_pass += 1

        note_str = "; ".join(notes) if notes else ""
        color_prefix = {
            "PASS": "",
            "REGRESSION": "REGRESSION ",
            "FAIL": "FAIL ",
            "SCOPE_LEAK": "SCOPE_LEAK ",
        }.get(status, "")
        print(f"{color_prefix}{note_str}")

        results.append({
            "kind": kind,
            "origin": origin["name"],
            "dest": dest["name"],
            "status": status,
            "baseline_distance_m": b_dist,
            "new_distance_m": n_dist,
            "new_code": n_code,
            "notes": notes,
        })
        time.sleep(REQUEST_DELAY_S)

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print("=" * 50)
    print(f"PASS:       {n_pass}")
    print(f"REGRESSION: {n_regression}")
    print(f"FAIL:       {n_fail}")
    print(f"SCOPE_LEAK: {n_scope_leak}")
    total_issues = n_regression + n_fail + n_scope_leak
    overall = "PASS" if total_issues == 0 else f"FAIL ({total_issues} issues)"
    print(f"OVERALL:    {overall}")
    print("=" * 50)

    out_path = Path("data/routing/baseline/regression_results.json")
    out_path.write_text(json.dumps({
        "osrm_url": args.osrm_url,
        "baseline_file": str(BASELINE_PATH),
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "summary": {"pass": n_pass, "regression": n_regression, "fail": n_fail, "scope_leak": n_scope_leak},
        "pairs": results,
    }, indent=2))
    print(f"Results saved to {out_path}")


if __name__ == "__main__":
    main()
