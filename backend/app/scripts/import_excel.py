import pandas as pd
import json
import re
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parents[3]
EXCEL_PATH = ROOT_DIR / "Data collection.xlsx"
FACILITIES_JSON_PATH = ROOT_DIR / "database" / "seed" / "facilities.json"

def parse_dms(dms_str):
    if pd.isna(dms_str) or not str(dms_str).strip():
        return None
    dms_str = str(dms_str).strip()
    # Handle different characters like 7̊˚15'21"
    matches = re.findall(r"(\d+(?:\.\d+)?)", dms_str)
    if len(matches) >= 3:
        deg = float(matches[0])
        min_ = float(matches[1])
        sec = float(matches[2])
        return round(deg + (min_ / 60) + (sec / 3600), 6)
    return None

def parse_fixtures(bathroom_str, sink, mirror, shower):
    fixtures = {}
    
    if pd.notna(sink) and str(sink).strip().isdigit():
        fixtures["sink"] = int(float(sink))
    if pd.notna(mirror) and str(mirror).strip().isdigit():
        fixtures["mirror"] = int(float(mirror))
    if pd.notna(shower) and str(shower).strip().isdigit():
        fixtures["shower"] = int(float(shower))
        
    if pd.isna(bathroom_str) or not str(bathroom_str).strip():
        return fixtures
        
    bathroom_str = str(bathroom_str).strip()
    
    normal_match = re.search(r"N-(\d+)", bathroom_str)
    attached_match = re.search(r"A-(\d+)", bathroom_str)
    
    if normal_match:
        fixtures["normal"] = int(normal_match.group(1))
    if attached_match:
        fixtures["attached"] = int(attached_match.group(1))
        
    if not normal_match and not attached_match and bathroom_str.isdigit():
        fixtures["normal"] = int(bathroom_str)
        
    return fixtures

def main():
    if not EXCEL_PATH.exists():
        print(f"Error: {EXCEL_PATH} not found.")
        return

    df = pd.read_excel(EXCEL_PATH)
    
    df = df.dropna(subset=['Location', 'Latitude', 'Longitude'], how='all')

    facilities = []
    
    for idx, row in df.iterrows():
        location = str(row.get('Location', '')).strip()
        if not location or location == "nan":
            continue
            
        lat = parse_dms(row.get('Latitude'))
        lon = parse_dms(row.get('Longitude'))
        
        if lat is None or lon is None:
            continue
            
        fixtures = parse_fixtures(
            row.get('Bathroom'),
            row.get('Sink'),
            row.get('Mirror'),
            row.get('Shower')
        )
        
        audience = "STAFF" if "staff" in location.lower() else "VISITOR"
        
        loc_lower = location.lower()
        is_female = "female" in loc_lower or "famale" in loc_lower or "women" in loc_lower or "ladies" in loc_lower
        is_male = "male" in loc_lower and not is_female
        is_gents = "gents" in loc_lower or "men" in loc_lower or is_male
        
        def create_facility(cat_code, suffix=""):
            name = location
            if suffix:
                name = f"{location} - {suffix}"
                
            return {
                "name": name,
                "location_name": location,
                "audience": audience,
                "latitude": lat,
                "longitude": lon,
                "fixtures": fixtures,
                "status": "OPEN",
                "rating": 4.0,
                "category_code": cat_code,
                "data_source": "REAL"
            }

        if is_female:
            facilities.append(create_facility("female"))
        elif is_gents:
            facilities.append(create_facility("male"))
        else:
            facilities.append(create_facility("male", "Men's"))
            facilities.append(create_facility("female", "Women's"))
            
    print(f"Parsed {len(facilities)} facilities.")
    
    with open(FACILITIES_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(facilities, f, indent=2)
        
    print(f"Written to {FACILITIES_JSON_PATH}")

if __name__ == "__main__":
    main()
