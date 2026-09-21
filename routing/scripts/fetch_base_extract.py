"""B1 — Download the Geofabrik Sri Lanka OSM PBF base extract.

Records sha256, file size, and the OSM timestamp from the .osm.pbf header
(via the osmium fileinfo JSON output if osmium is available, else a note).

Usage:
    python routing/scripts/fetch_base_extract.py [--url URL] [--out PATH]
"""

import argparse
import hashlib
import json
import subprocess
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_URL = "https://download.geofabrik.de/asia/sri-lanka-latest.osm.pbf"
DEFAULT_OUT  = "data/routing/raw/sri-lanka-latest.osm.pbf"
CHUNK_SIZE   = 1024 * 1024  # 1 MB


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "geoai-fetch/1.0"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        start = time.time()
        with out.open("wb") as f:
            while True:
                chunk = resp.read(CHUNK_SIZE)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                elapsed = time.time() - start
                speed_kb = (downloaded / elapsed / 1024) if elapsed > 0 else 0
                pct = (downloaded / total * 100) if total else 0
                print(
                    f"\r  {downloaded/1024/1024:.1f} MB / {total/1024/1024:.1f} MB"
                    f"  ({pct:.0f}%)  {speed_kb:.0f} KB/s",
                    end="",
                    flush=True,
                )
    print()


def get_osm_timestamp(pbf_path: Path) -> str:
    """Try to read the OSM timestamp from the PBF header via osmium fileinfo."""
    try:
        result = subprocess.run(
            ["osmium", "fileinfo", "--json", str(pbf_path)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            info = json.loads(result.stdout)
            return info.get("header", {}).get("option", {}).get("osmosis_replication_timestamp", "unknown")
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return "osmium not available — timestamp unknown; check Geofabrik metadata page"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--skip-download", action="store_true",
                        help="Skip download if file already exists (still verifies sha256)")
    args = parser.parse_args()

    out = Path(args.out)

    if out.exists() and args.skip_download:
        print(f"File already exists: {out} ({out.stat().st_size / 1024 / 1024:.1f} MB). Computing sha256...")
    else:
        if out.exists():
            print(f"File exists but --skip-download not set. Re-downloading...")
        download(args.url, out)

    size_bytes = out.stat().st_size
    print(f"Computing sha256 of {size_bytes / 1024 / 1024:.1f} MB file...", flush=True)
    digest = sha256_file(out)
    print(f"sha256: {digest}")

    timestamp = get_osm_timestamp(out)

    record = {
        "url": args.url,
        "local_path": str(out),
        "size_bytes": size_bytes,
        "sha256": digest,
        "osm_timestamp": timestamp,
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
    }

    manifest_path = out.parent / "base_extract_manifest.json"
    manifest_path.write_text(json.dumps(record, indent=2))
    print(f"\nManifest written to {manifest_path}")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
