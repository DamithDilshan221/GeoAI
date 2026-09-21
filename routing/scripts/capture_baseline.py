"""A5 — Capture baseline routes against the current public OSRM demo.

Calls every pair defined in verification_pairs.yaml (or hard-coded pairs when
the yaml does not yet exist) against the currently configured OSRM_BASE_URL,
with a 1-request-per-second rate limit.  Saves raw JSON responses to
data/routing/baseline/public_demo.json.

Usage:
    python routing/scripts/capture_baseline.py [--osrm-url URL]
"""

import json
import time
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Verification pairs from §6 Phase A4
# ---------------------------------------------------------------------------

ORIGINS = [
    {"name": "campus_reference",          "lat": 7.2545,    "lon": 80.5965},
    {"name": "alwis_roundabout",          "lat": 7.258475,  "lon": 80.599507},
    {"name": "peradeniya_road_junction",  "lat": 7.2678638, "lon": 80.5968155},
    {"name": "trunk_west_end",            "lat": 7.2641396, "lon": 80.5931847},
    {"name": "akbar_bridge_north",        "lat": 7.2548901, "lon": 80.5953713},
    {"name": "river_drive_north",         "lat": 7.2716512, "lon": 80.5937858},
    {"name": "south_drive_north",         "lat": 7.2680963, "lon": 80.594686},
]

DESTINATIONS = [
    {"name": "gym_mens",                  "lat": 7.256062,  "lon": 80.595166},
    {"name": "ict_mens",                  "lat": 7.256578,  "lon": 80.595771},
    {"name": "ma_womens",                 "lat": 7.255044,  "lon": 80.597754},
    {"name": "nat_1f_mens",               "lat": 7.254825,  "lon": 80.599122},
    {"name": "near_library_mens",         "lat": 7.25323,   "lon": 80.592642},
    {"name": "akbar_corridor_female",     "lat": 7.252764,  "lon": 80.591776},
    {"name": "drawing_office_gents",      "lat": 7.254636,  "lon": 80.591703},
    {"name": "postgrad_1f_mens",          "lat": 7.255833,  "lon": 80.599722},
]

FAR_PAIRS = [
    {
        "name": "colombo_fort_to_galle_face",
        "origin": {"name": "colombo_fort_station", "lat": 6.9335, "lon": 79.8500},
        "dest":   {"name": "galle_face_green",     "lat": 6.9270, "lon": 79.8450},
    },
    {
        "name": "galle_fort_to_galle_bus_stand",
        "origin": {"name": "galle_fort_clock_tower", "lat": 6.0287, "lon": 80.2168},
        "dest":   {"name": "galle_bus_stand",         "lat": 6.0329, "lon": 80.2149},
    },
]


def fetch_route(osrm_url: str, origin: dict, dest: dict) -> dict:
    url = (
        f"{osrm_url}/route/v1/foot/"
        f"{origin['lon']},{origin['lat']};{dest['lon']},{dest['lat']}"
        "?overview=full&geometries=geojson&steps=true"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "geoai-baseline/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return {"status": resp.status, "body": json.loads(resp.read()), "url": url, "error": None}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "body": None, "url": url, "error": str(e)}
    except Exception as e:
        return {"status": None, "body": None, "url": url, "error": str(e)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--osrm-url", default="https://router.project-osrm.org")
    args = parser.parse_args()

    output_path = Path("data/routing/baseline/public_demo.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    results = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "osrm_url": args.osrm_url,
        "pairs": [],
    }

    # Campus pairs (all origins × all destinations)
    all_pairs = []
    for orig in ORIGINS:
        for dest in DESTINATIONS:
            all_pairs.append(("campus", orig, dest))

    # Far-outside pairs
    for fp in FAR_PAIRS:
        all_pairs.append(("far_outside", fp["origin"], fp["dest"]))

    print(f"Capturing {len(all_pairs)} pairs against {args.osrm_url}")

    for i, (kind, orig, dest) in enumerate(all_pairs):
        print(f"  [{i+1}/{len(all_pairs)}] {kind}: {orig['name']} -> {dest['name']}", end=" ... ", flush=True)
        result = fetch_route(args.osrm_url, orig, dest)

        pair_record = {
            "kind": kind,
            "origin": orig,
            "dest": dest,
            "status": result["status"],
            "url": result["url"],
            "error": result["error"],
        }

        body = result.get("body")
        if body and body.get("code") == "Ok" and body.get("routes"):
            r = body["routes"][0]
            pair_record["code"] = "Ok"
            pair_record["distance_m"] = r["distance"]
            pair_record["duration_s"] = r["duration"]
            # Store geometry for later comparison
            pair_record["geometry_coords"] = r["geometry"]["coordinates"]
            print(f"OK  {r['distance']:.0f}m  {r['duration']:.0f}s")
        else:
            pair_record["code"] = body.get("code") if body else "NO_RESPONSE"
            pair_record["distance_m"] = None
            pair_record["duration_s"] = None
            pair_record["geometry_coords"] = None
            print(f"FAIL code={pair_record['code']} error={result['error']}")

        results["pairs"].append(pair_record)

        if i < len(all_pairs) - 1:
            time.sleep(1.0)  # ≤1 req/s

    output_path.write_text(json.dumps(results, indent=2))
    print(f"\nSaved to {output_path}")

    # Summary
    ok = sum(1 for p in results["pairs"] if p.get("code") == "Ok")
    fail = len(results["pairs"]) - ok
    print(f"Summary: {ok} Ok, {fail} failed")


if __name__ == "__main__":
    main()
