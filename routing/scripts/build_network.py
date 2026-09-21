"""Phase C / D — build_network.py

Merges campus footpath LineStrings from Washroommap.geojson into the Sri Lanka
OSM base PBF to produce additions.osm and an augmented PBF ready for osrm-extract.

Strategy
--------
1. Parse Washroommap.geojson for LineString features.
2. Apply D2 selection rules (footpath_rules.yaml):
   - Always add:  footway, path, steps, pedestrian
   - Add if foot allowed:  cycleway (remap to path), track
   - Exclude:  access in {private, no, customers, delivery, permit}
   - Never add:  service, residential, unclassified, tertiary, primary,
                 trunk, trunk_link, living_street, secondary
3. Assign synthetic node and way IDs starting from 5 000 000 000 000 000.
   - Deduplicate coordinates across ways so connected footpaths share nodes.
   - Remap cycleway -> path and record original_highway=cycleway.
4. Output:
   - data/routing/build/additions.osm          : synthetic OSM XML
   - data/routing/build/network_report.json    : classification report
   - data/routing/build/augmented.osm.pbf      : merged base PBF + additions
"""

import json
import math
import re
import hashlib
import argparse
import sys
import time
from pathlib import Path
from collections import Counter, defaultdict

try:
    import osmium
except ImportError:
    osmium = None

# ── Config defaults ───────────────────────────────────────────────────────────
DEFAULT_RULES_PATH  = "routing/config/footpath_rules.yaml"
DEFAULT_GEOJSON     = "data/routing/source/Washroommap.geojson"
DEFAULT_BASE_PBF    = "data/routing/raw/sri-lanka-latest.osm.pbf"
DEFAULT_OUTPUT_DIR  = Path("data/routing/build")
SYNTHETIC_ID_START  = 900_000_000_000

ALWAYS_ADD          = {"footway", "path", "steps", "pedestrian"}
ADD_IF_FOOT_ALLOWED = {"cycleway", "track"}
NEVER_ADD           = {"service", "residential", "unclassified", "tertiary",
                       "primary", "primary_link", "trunk", "trunk_link",
                       "living_street", "secondary", "secondary_link",
                       "tertiary_link"}
EXCLUDE_ACCESS      = {"private", "no", "customers", "delivery", "permit"}

CYCLEWAY_REMAP = "path"
COORD_DECIMALS = 7


def load_rules(path: str) -> dict:
    """Minimal YAML key-value loader."""
    rules = {
        "always_add":          list(ALWAYS_ADD),
        "add_if_foot_allowed": list(ADD_IF_FOOT_ALLOWED),
        "never_add":           list(NEVER_ADD),
        "exclude_access":      list(EXCLUDE_ACCESS),
        "synthetic_id_start":  SYNTHETIC_ID_START,
        "approved_overrides":  [],
    }
    try:
        content = Path(path).read_text(encoding="utf-8")
        m = re.search(r"synthetic_id_start:\s*(\d+)", content)
        if m:
            rules["synthetic_id_start"] = int(m.group(1))
    except Exception:
        pass
    return rules


def coord_sha1(coords: list[list[float]]) -> str:
    normalized = json.dumps([[round(c[0], COORD_DECIMALS), round(c[1], COORD_DECIMALS)]
                             for c in coords], sort_keys=True)
    return hashlib.sha1(normalized.encode()).hexdigest()[:12]


def classify_way(
    props: dict | None,
    rules: dict,
    *,
    index: int = 0,
) -> tuple[str, str]:
    if props is None:
        return "skip_null_props", "properties=null"

    hw = props.get("highway", "").strip() if isinstance(props.get("highway"), str) else ""
    access = props.get("access", "").strip() if isinstance(props.get("access"), str) else ""
    foot = props.get("foot", "").strip() if isinstance(props.get("foot"), str) else ""

    if not hw:
        if foot in ("designated", "yes", "permissive"):
            return "add", f"no highway tag but foot={foot}"
        return "skip_no_highway", "no highway tag and no foot tag"

    always_add_set = set(rules.get("always_add", ALWAYS_ADD))
    add_if_foot_set = set(rules.get("add_if_foot_allowed", ADD_IF_FOOT_ALLOWED))
    never_add_set = set(rules.get("never_add", NEVER_ADD))
    exclude_access_set = set(rules.get("exclude_access", EXCLUDE_ACCESS))

    if access in exclude_access_set:
        return "needs_approval", f"access={access}"

    if hw in never_add_set:
        return "skip_never_add", f"highway={hw} is never-add class"

    if hw in always_add_set:
        return "add", f"highway={hw} is always-add class"

    if hw in add_if_foot_set:
        allowed_foot = {"designated", "yes", "permissive", "destination", "permit"}
        if foot in allowed_foot:
            return "add", f"highway={hw} with foot={foot}"
        if not foot:
            return "add", f"highway={hw} no foot tag (absent=allowed per D2)"
        return "skip_never_add", f"highway={hw} foot={foot} not in allowed set"

    return "needs_approval", f"highway={hw} not in any explicit class"


def write_additions_osm(
    ways_to_add: list[dict],
    synthetic_id_start: int,
    output_path: Path,
) -> tuple[int, int, dict[tuple[float, float], int], list[dict]]:
    """
    Write an OSM XML file with synthetic ways + deduplicated nodes.
    Returns (n_ways_written, n_new_nodes_created, coord_to_node_id, processed_ways).
    """
    next_id = synthetic_id_start
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<osm version="0.6" generator="geoai-build-network/1.0">',
    ]

    coord_to_node_id: dict[tuple[float, float], int] = {}
    all_nodes: list[str] = []
    all_ways: list[str] = []
    processed_ways: list[dict] = []

    for way_info in ways_to_add:
        coords   = way_info["coords"]
        props    = way_info["props"] or {}
        hw       = props.get("highway", "")
        ls_index = way_info["ls_index"]

        effective_hw = CYCLEWAY_REMAP if hw == "cycleway" else hw

        node_ids: list[int] = []
        for c in coords:
            lon_r = round(c[0], COORD_DECIMALS)
            lat_r = round(c[1], COORD_DECIMALS)
            key   = (lon_r, lat_r)

            if key in coord_to_node_id:
                node_ids.append(coord_to_node_id[key])
            else:
                node_id = next_id
                next_id += 1
                coord_to_node_id[key] = node_id
                all_nodes.append(
                    f'  <node id="{node_id}" lat="{lat_r}" lon="{lon_r}" '
                    f'version="1" visible="true"/>'
                )
                node_ids.append(node_id)

        way_id = next_id
        next_id += 1

        tags_lines = []
        tags_lines.append(f'    <tag k="highway" v="{effective_hw}"/>')
        if hw == "cycleway":
            tags_lines.append('    <tag k="original_highway" v="cycleway"/>')

        copy_tags = ["name", "surface", "foot", "bicycle", "access",
                     "layer", "bridge", "tunnel", "incline", "width",
                     "wheelchair", "lit"]
        for tag in copy_tags:
            val = props.get(tag)
            if val:
                safe_val = str(val).replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
                tags_lines.append(f'    <tag k="{tag}" v="{safe_val}"/>')

        tags_lines.append('    <tag k="source" v="Washroommap.geojson"/>')
        tags_lines.append('    <tag k="campus_footpath" v="yes"/>')
        tags_lines.append(f'    <tag k="campus_ls_index" v="{ls_index}"/>')

        way_lines = [f'  <way id="{way_id}" version="1" visible="true">']
        way_lines += [f'    <nd ref="{nid}"/>' for nid in node_ids]
        way_lines += tags_lines
        way_lines.append('  </way>')
        all_ways.append("\n".join(way_lines))

        processed_ways.append({
            "way_id": way_id,
            "ls_index": ls_index,
            "node_ids": node_ids,
            "highway": effective_hw,
            "coords": coords,
            "props": props
        })

    lines.extend(all_nodes)
    lines.extend(all_ways)
    lines.append('</osm>')

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return len(all_ways), len(coord_to_node_id), coord_to_node_id, processed_ways


def build_augmented_pbf(
    base_pbf_path: Path,
    additions_osm_path: Path,
    output_pbf_path: Path,
) -> None:
    """
    Stream base PBF + additions.osm into augmented.osm.pbf in strictly valid
    OSM order: all nodes, then all ways, then all relations.
    """
    if osmium is None:
        raise RuntimeError("osmium python module is required for augmented PBF generation")

    print(f"\nBuilding augmented PBF: {output_pbf_path}...")
    t0 = time.time()
    
    writer = osmium.SimpleWriter(str(output_pbf_path), overwrite=True)

    class NodeHandler(osmium.SimpleHandler):
        def node(self, n):
            writer.add_node(n)

    class WayHandler(osmium.SimpleHandler):
        def way(self, w):
            writer.add_way(w)

    class RelHandler(osmium.SimpleHandler):
        def relation(self, r):
            writer.add_relation(r)

    print("  1/3 Streaming nodes (base + additions)...")
    NodeHandler().apply_file(str(base_pbf_path))
    NodeHandler().apply_file(str(additions_osm_path))

    print("  2/3 Streaming ways (base + additions)...")
    WayHandler().apply_file(str(base_pbf_path))
    WayHandler().apply_file(str(additions_osm_path))

    print("  3/3 Streaming relations (base)...")
    RelHandler().apply_file(str(base_pbf_path))

    writer.close()
    
    elapsed = time.time() - t0
    size_mb = output_pbf_path.stat().st_size / (1024 * 1024)
    print(f"  Augmented PBF written in {elapsed:.1f}s ({size_mb:.1f} MB)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase C/D build_network.py")
    parser.add_argument("--dry-run", action="store_true", help="Report only")
    parser.add_argument("--rules", default=DEFAULT_RULES_PATH)
    parser.add_argument("--geojson", default=DEFAULT_GEOJSON)
    parser.add_argument("--base-pbf", default=DEFAULT_BASE_PBF)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rules = load_rules(args.rules)

    print("=== Phase C/D — build_network.py ===")
    print(f"GeoJSON:   {args.geojson}")
    print(f"Base PBF:  {args.base_pbf}")
    print(f"Rules:     {args.rules}")
    print()

    gj_path = Path(args.geojson)
    if not gj_path.exists():
        print(f"ERROR: GeoJSON not found: {gj_path}")
        sys.exit(1)

    gj = json.loads(gj_path.read_text(encoding="utf-8"))
    ls_feats = [f for f in gj["features"]
                if f.get("geometry") and f["geometry"]["type"] == "LineString"]
    print(f"LineStrings found in GeoJSON: {len(ls_feats)}")

    report: list[dict] = []
    to_add: list[dict] = []

    for i, feat in enumerate(ls_feats):
        props  = feat.get("properties")
        coords = feat["geometry"]["coordinates"]
        hw     = (props or {}).get("highway", "(none)")
        sha1   = coord_sha1(coords)

        decision, reason = classify_way(props, rules, index=i)

        rec = {
            "ls_index":    i,
            "highway":     hw,
            "sha1":        sha1,
            "n_vertices":  len(coords),
            "decision":    decision,
            "reason":      reason,
        }
        report.append(rec)

        if decision == "add":
            to_add.append({"ls_index": i, "coords": coords, "props": props})

    dec_counts = Counter(r["decision"] for r in report)
    print(f"\n{'Decision':25s} {'Count':>6s}")
    print("-" * 34)
    for dec, cnt in sorted(dec_counts.items(), key=lambda x: -x[1]):
        print(f"  {dec:23s} {cnt:6d}")

    report_path = out_dir / "network_report.json"
    report_path.write_text(json.dumps({"summary": dict(dec_counts), "ways": report}, indent=2), encoding="utf-8")
    print(f"\nNetwork report saved to {report_path}")

    if args.dry_run:
        print("Dry run complete.")
        return

    # Write additions.osm
    additions_path = out_dir / "additions.osm"
    n_ways, n_nodes, coord_map, proc_ways = write_additions_osm(
        to_add,
        rules.get("synthetic_id_start", SYNTHETIC_ID_START),
        additions_path,
    )
    print(f"\nAdditions written to {additions_path}:")
    print(f"  {n_ways} ways written, {n_nodes} unique synthetic nodes created")

    # Build augmented PBF
    base_pbf = Path(args.base_pbf)
    aug_pbf = out_dir / "augmented.osm.pbf"
    if base_pbf.exists():
        build_augmented_pbf(base_pbf, additions_path, aug_pbf)
    else:
        print(f"WARNING: Base PBF not found at {base_pbf}. Skipping augmented PBF.")

    print("\nPhase C & D complete! Ready for Phase E (build_osrm.ps1).")


if __name__ == "__main__":
    main()
