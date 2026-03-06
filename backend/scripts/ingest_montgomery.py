"""
Montgomery, AL data ingestion script.

Reads CSV files from data/raw/ and inserts records into the UrbanPulse
database according to the column mapping in config/cities/montgomery.json.

Usage:
    cd backend/
    python -m scripts.ingest_montgomery
"""

import csv
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlmodel import Session, SQLModel, create_engine

from app.models.property import Property, Incident, CityProject

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent.parent          # workspace root
CONFIG_PATH = ROOT_DIR / "config" / "cities" / "montgomery.json"
DATA_DIR = ROOT_DIR / "backend" / "data" / "raw"
DB_PATH = Path(__file__).resolve().parent.parent / "urbanpulse.db"
DB_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DB_URL, echo=False, connect_args={"check_same_thread": False})


def load_config() -> dict:
    """Load the Montgomery city configuration."""
    with open(CONFIG_PATH) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Ingest parcels → Property table
# ---------------------------------------------------------------------------

def ingest_parcels(session: Session, config: dict) -> int:
    """Read parcels CSV and insert Property records.

    Returns the number of rows inserted.
    """
    csv_path = ROOT_DIR / "backend" / config["datasets"]["parcels"]["local_file"]
    col_map = config["column_mapping"]["parcels"]

    if not csv_path.exists():
        print(f"[!] Parcels CSV not found: {csv_path}")
        print("    Download or place the parcels CSV at the above path.")
        return 0

    count = 0
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                lat = float(row.get(col_map["latitude"], 0) or 0)
                lng = float(row.get(col_map["longitude"], 0) or 0)
                if lat == 0 or lng == 0:
                    continue  # skip rows without coordinates

                prop = Property(
                    parcel_id=row.get(col_map["parcel_id"], "").strip(),
                    address=row.get(col_map["address"], "").strip(),
                    latitude=lat,
                    longitude=lng,
                    property_type=row.get(col_map.get("property_type", ""), "unknown").strip().lower() or "unknown",
                    zoning=row.get(col_map.get("zoning", ""), None) or None,
                    is_vacant=str(row.get(col_map.get("is_vacant", ""), "")).strip().upper() in ("Y", "YES", "TRUE", "1"),
                    lot_size_sqft=_safe_float(row.get(col_map.get("lot_size_sqft", ""))),
                    assessed_value=_safe_float(row.get(col_map.get("assessed_value", ""))),
                    year_built=_safe_int(row.get(col_map.get("year_built", ""))),
                    neighborhood=row.get(col_map.get("neighborhood", ""), None) or None,
                )
                session.add(prop)
                count += 1

                # Commit in batches
                if count % 500 == 0:
                    session.commit()
                    print(f"    ... {count} parcels inserted")

            except Exception as e:
                print(f"    [WARN] Skipping row: {e}")
                continue

    session.commit()
    return count


# ---------------------------------------------------------------------------
# Ingest incidents → Incident table
# ---------------------------------------------------------------------------

def ingest_incidents(session: Session, config: dict) -> int:
    """Read incidents CSV and insert Incident records."""
    csv_path = ROOT_DIR / "backend" / config["datasets"]["incidents"]["local_file"]

    if not csv_path.exists():
        print(f"[!] Incidents CSV not found: {csv_path}")
        print("    Download or place the incidents CSV at the above path.")
        return 0

    count = 0
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                lat = float(row.get("LATITUDE", 0) or 0)
                lng = float(row.get("LONGITUDE", 0) or 0)
                if lat == 0 or lng == 0:
                    continue

                inc = Incident(
                    incident_id=row.get("INCIDENT_ID", "").strip() or None,
                    incident_type=row.get("INCIDENT_TYPE", "unknown").strip().lower(),
                    latitude=lat,
                    longitude=lng,
                    neighborhood=row.get("NEIGHBORHOOD", None) or None,
                    severity=row.get("SEVERITY", None) or None,
                )
                session.add(inc)
                count += 1

                if count % 500 == 0:
                    session.commit()
                    print(f"    ... {count} incidents inserted")

            except Exception as e:
                print(f"    [WARN] Skipping incident row: {e}")
                continue

    session.commit()
    return count


# ---------------------------------------------------------------------------
# Ingest city projects → CityProject table
# ---------------------------------------------------------------------------

def ingest_city_projects(session: Session, config: dict) -> int:
    """Read city projects CSV and insert CityProject records."""
    csv_path = ROOT_DIR / "backend" / config["datasets"]["city_projects"]["local_file"]

    if not csv_path.exists():
        print(f"[!] City projects CSV not found: {csv_path}")
        print("    Download or place the city projects CSV at the above path.")
        return 0

    count = 0
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cp = CityProject(
                    project_name=row.get("PROJECT_NAME", "").strip(),
                    project_type=row.get("PROJECT_TYPE", None) or None,
                    status=row.get("STATUS", "planned").strip().lower(),
                    latitude=_safe_float(row.get("LATITUDE")),
                    longitude=_safe_float(row.get("LONGITUDE")),
                    budget=_safe_float(row.get("BUDGET")),
                    description=row.get("DESCRIPTION", None) or None,
                )
                session.add(cp)
                count += 1
            except Exception as e:
                print(f"    [WARN] Skipping project row: {e}")
                continue

    session.commit()
    return count


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_float(val) -> float | None:
    """Convert value to float, returning None on failure."""
    if val is None:
        return None
    try:
        return float(str(val).replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def _safe_int(val) -> int | None:
    """Convert value to int, returning None on failure."""
    if val is None:
        return None
    try:
        return int(float(str(val).replace(",", "").strip()))
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("  UrbanPulse — Montgomery, AL  Data Ingestion")
    print("=" * 60)

    # Load config
    if not CONFIG_PATH.exists():
        print(f"[!] Config not found: {CONFIG_PATH}")
        sys.exit(1)

    config = load_config()
    print(f"[+] Loaded config for {config['city_name']}, {config['state']}")

    # Create tables
    SQLModel.metadata.create_all(engine)
    print(f"[+] Database ready at: {DB_PATH}")

    print(f"\n[i] Looking for data files in: {DATA_DIR}")
    print()

    with Session(engine) as session:
        # Parcels
        print("[*] Ingesting parcels...")
        n_parcels = ingest_parcels(session, config)
        print(f"    => {n_parcels} parcels ingested")

        # Incidents
        print("[*] Ingesting incidents...")
        n_incidents = ingest_incidents(session, config)
        print(f"    => {n_incidents} incidents ingested")

        # City projects
        print("[*] Ingesting city projects...")
        n_projects = ingest_city_projects(session, config)
        print(f"    => {n_projects} city projects ingested")

    print("\n" + "=" * 60)
    print("  Required data files:")
    print("-" * 60)
    for key, ds in config["datasets"].items():
        full_path = ROOT_DIR / "backend" / ds["local_file"]
        status = "FOUND" if full_path.exists() else "MISSING"
        print(f"  [{status}]  {ds['local_file']:<35s}  {ds['description']}")
    print("=" * 60)
    print("\nTo obtain data files:")
    print(f"  1. Visit {config['open_data_portal']}")
    print("  2. Search for each dataset listed above")
    print("  3. Export as CSV and place in backend/data/raw/")
    print("  4. Re-run this script: python -m scripts.ingest_montgomery")


if __name__ == "__main__":
    main()
