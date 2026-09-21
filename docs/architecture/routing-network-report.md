# Campus Footpath Routing Network & Verification Report (Phase G)

**Project:** GeoAI / RestNav — Campus Washroom Finder (University of Peradeniya)  
**Date:** 2026-09-21  
**Status:** Native OSRM MLD Augmented Build Verified  

---

## 1. Network Construction & Ingestion Summary

- **Source GeoJSON:** `data/routing/source/Washroommap.geojson` (165 LineStrings)
- **Base OSM Extract:** `data/routing/raw/sri-lanka-latest.osm.pbf` (Geofabrik Sri Lanka, 137.6 MB)
- **Classification Rules:** Defined in `routing/config/footpath_rules.yaml`

### Classification Decisions Breakdown:
| Decision Class | Count | Description / Rules Applied |
| :--- | :--- | :--- |
| `add` | **51** | Valid campus footpaths (`footway`, `path`, `steps`, `pedestrian`, `cycleway` remapped to `path`) |
| `skip_never_add` | **91** | Roads/driveways already present in base OSM (`service`, `residential`, `primary`, etc.) |
| `skip_no_highway` | **10** | Features without `highway` or `foot` tag |
| `skip_null_props` | **8** | Geometry features with empty/null property dictionaries |
| `needs_approval` | **5** | Ambiguous access/tracks requiring explicit administrative override |
| **Total Features** | **165** | Full GeoJSON LineString catalog |

- **Synthetic Additions (`additions.osm`):**
  - Total synthetic ways: **51**
  - Total unique synthetic nodes: **228** (with exact coordinate deduplication)
  - Synthetic ID range: `900,000,000,000` to `900,000,000,228` (safely below OSRM 40-bit node ID limit)

---

## 2. OSRM Native Binary Architecture

- **OSRM Version:** `v26.9.0` (`win32-x64` Release)
- **Runtime:** Native Windows executables (`osrm-extract.exe`, `osrm-partition.exe`, `osrm-customize.exe`, `osrm-routed.exe`)
- **Algorithm:** Multi-Level Dijkstra (MLD)
- **Profile:** Public `foot.lua` (10,682 bytes, SHA-256 verified)
- **Active Ports:**
  - Augmented Campus Router: `http://localhost:5001`
  - Base-only Reference Router: `http://localhost:5002`
  - FastAPI Backend: `http://localhost:8000`
  - Frontend Client: `http://localhost:5173`

---

## 3. Key Deviations & Technical Rationale

1. **Port 5001 vs Port 5000:**
   - *Rationale:* Windows developer environments frequently bind port 5000 to Windows UPnP/SSDP, Apple AirPlay, or background services. Port 5001 avoids port collision errors (`WSAEADDRINUSE`).
2. **Synthetic Node ID `900,000,000,000` vs `5,000,000,000,000,000`:**
   - *Technical Constraint:* Upstream OSRM compiles with 40-bit packed node IDs (`PACKED_OSM_ID_BITS = 40`). Maximum allowable node ID is $2^{40}-1 \approx 1.0995 \times 10^{12}$. IDs $\ge 1.1\text{T}$ trigger immediate fatal compilation errors in `osrm-extract`. $900\text{B}$ is strictly required and safely fits within 40-bit representation.
3. **58-Pair Standard Regression vs 200+ Outside Invariance Suite:**
   - *Rationale:* `verification_pairs.yaml` maintains a 58-pair fast regression test for CI/CD, while the dynamic 210-pair seeded-random comparison suite tests outside-footprint invariance across the island.

---

## 4. Verification & Quality Gate Results

| Test Category | Command / Harness | Result | Metrics |
| :--- | :--- | :--- | :--- |
| **Augmented Footpaths** | Direct OSRM + Backend `/routes` | **PASS** | `code="Ok"`, `source="network"` |
| **Outside Invariance** | 210 Seeded Pairs (5001 vs 5002) | **PASS** | 210/210 exact matches (0.000m max delta) |
| **OSM Transitions** | 5 Highway $\rightarrow$ Campus Pairs | **PASS** | Continuous maneuver & node chains |
| **Akbar Bridge Geometry** | OSRM Maneuvers + GeoJSON Coords | **PASS** | Named step + 507m route vs 3.76km detour |
| **Full Island Coverage** | Colombo $\rightarrow$ Kandy (115 km) | **PASS** | 137.6MB PBF, full graph preserved |
| **CORS Validation** | Origin: `http://localhost:5173` | **PASS** | Backend & OSRM allow origin |
| **Engine Fallback** | Up $\rightarrow$ Down $\rightarrow$ Restarted | **PASS** | `network` $\rightarrow$ `straight_line_estimate` $\rightarrow$ `network` |
| **Backend Unit Tests** | `pytest backend/tests` | **PASS** | 202/202 passed (0 failures) |
| **Backend Lint** | `ruff check backend` | **PASS** | All checks passed |
| **Frontend Unit Tests** | `vitest run` | **PASS** | 24/24 files, 129/129 passed |
| **Frontend Lint** | `eslint .` | **PASS** | 0 errors, 0 warnings |
| **Frontend Build** | `tsc -b && vite build` | **PASS** | Production bundle compiled |
| **Repeatability** | Deterministic dual run & SHA-256 | **PASS** | Identical SHA-256 hash & reports |
