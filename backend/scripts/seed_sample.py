"""
Seed script: populates the UrbanPulse database with realistic sample data
for Montgomery, AL.

Usage:
    cd backend/
    python -m scripts.seed_sample
"""

import random
import sys
import os
from datetime import datetime, timedelta

# Ensure the backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlmodel import Session, SQLModel, create_engine

from app.models.property import (
    Property, PropertyScore, WebSignal, Incident,
    ServiceLocation, CityProject, Watchlist,
)

# ---------------------------------------------------------------------------
# Database setup — uses a local SQLite file next to the backend dir
# ---------------------------------------------------------------------------

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "urbanpulse.db")
DB_URL = f"sqlite:///{os.path.abspath(DB_PATH)}"

engine = create_engine(DB_URL, echo=False, connect_args={"check_same_thread": False})

# ---------------------------------------------------------------------------
# Realistic Montgomery, AL reference data
# ---------------------------------------------------------------------------

NEIGHBORHOODS = [
    "Downtown", "Capitol Heights", "Cloverdale", "Old Cloverdale",
    "Midtown", "Normandale", "Highland Park", "Garden District",
    "Arrowhead", "Dalraida", "Chisholm", "McGehee Estates",
    "Woodmere", "Ridgewood", "Haardt", "Zelda Road Corridor",
    "Eastern Boulevard Corridor", "Atlanta Highway Corridor",
    "West Montgomery", "North Montgomery",
]

# Approximate bounding box per neighborhood (lat, lng center + small jitter)
NEIGHBORHOOD_COORDS = {
    "Downtown":                     (32.3770, -86.3085),
    "Capitol Heights":              (32.3730, -86.2950),
    "Cloverdale":                   (32.3600, -86.3100),
    "Old Cloverdale":               (32.3560, -86.3130),
    "Midtown":                      (32.3650, -86.3020),
    "Normandale":                   (32.3680, -86.2860),
    "Highland Park":                (32.3720, -86.3200),
    "Garden District":              (32.3580, -86.3050),
    "Arrowhead":                    (32.3880, -86.2550),
    "Dalraida":                     (32.3910, -86.2680),
    "Chisholm":                     (32.3500, -86.3400),
    "McGehee Estates":              (32.3420, -86.3300),
    "Woodmere":                     (32.3460, -86.2900),
    "Ridgewood":                    (32.3530, -86.2700),
    "Haardt":                       (32.3700, -86.2500),
    "Zelda Road Corridor":          (32.3760, -86.2400),
    "Eastern Boulevard Corridor":   (32.3830, -86.2300),
    "Atlanta Highway Corridor":     (32.3950, -86.2200),
    "West Montgomery":              (32.3650, -86.3500),
    "North Montgomery":             (32.4050, -86.3100),
}

STREET_NAMES = [
    "Dexter Ave", "Court St", "Perry St", "Monroe St", "Adams Ave",
    "Hull St", "Lawrence St", "Fairview Ave", "Felder Ave", "South Blvd",
    "Bell St", "Jeff Davis Ave", "Madison Ave", "Holt St", "Cleveland Ave",
    "Norman Bridge Rd", "Atlanta Hwy", "Eastern Blvd", "Zelda Rd",
    "Troy Hwy", "Mobile Hwy", "Mt Meigs Rd", "Ann St", "High St",
    "Molton St", "Bibb St", "Washington Ave", "Commerce St", "Tallapoosa St",
    "Coosa St", "Rosa Parks Ave", "Ripley St", "Narrow Lane Rd",
    "Woodmere Blvd", "Vaughn Rd", "Taylor Rd", "Coliseum Blvd",
    "McGehee Rd", "Mulberry St", "Goldthwaite St",
]

ZONING_CODES = ["R-1", "R-2", "R-3", "C-1", "C-2", "C-3", "M-1", "MU-1", "PD", "I-1"]

PROPERTY_TYPES = ["residential", "commercial", "mixed", "vacant_land"]

INCIDENT_TYPES = [
    "theft", "vandalism", "assault", "burglary", "traffic_accident",
    "noise_complaint", "trespassing", "fraud", "drug_activity", "arson",
]

SERVICE_TYPES = ["grocery", "clinic", "park", "school", "daycare", "library"]


def _jitter(base: float, spread: float = 0.004) -> float:
    """Add random jitter to a coordinate."""
    return base + random.uniform(-spread, spread)


def _random_dt(days_back: int = 365) -> datetime:
    """Return a random datetime within the last `days_back` days."""
    return datetime.utcnow() - timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )


# ---------------------------------------------------------------------------
# Seed functions
# ---------------------------------------------------------------------------

def seed_properties(session: Session) -> list[Property]:
    """Insert 50 realistic properties."""
    properties: list[Property] = []
    for i in range(50):
        nbhd = random.choice(NEIGHBORHOODS)
        center = NEIGHBORHOOD_COORDS[nbhd]
        ptype = random.choices(
            PROPERTY_TYPES,
            weights=[0.40, 0.30, 0.15, 0.15],
            k=1,
        )[0]
        is_vacant = ptype == "vacant_land" or random.random() < 0.15
        is_city_owned = random.random() < 0.10
        year = random.randint(1920, 2022) if not is_vacant else None
        lot = round(random.uniform(2000, 40000), 0)
        bldg = round(lot * random.uniform(0.2, 0.7), 0) if not is_vacant else None
        assessed = round(random.uniform(15000, 950000), 2) if not is_vacant else round(random.uniform(5000, 80000), 2)

        street_num = random.randint(100, 4500)
        street = random.choice(STREET_NAMES)
        address = f"{street_num} {street}"

        prop = Property(
            parcel_id=f"MG-{random.randint(10000, 99999)}-{random.randint(100, 999)}",
            address=address,
            latitude=_jitter(center[0]),
            longitude=_jitter(center[1]),
            property_type=ptype,
            zoning=random.choice(ZONING_CODES),
            is_vacant=is_vacant,
            is_city_owned=is_city_owned,
            lot_size_sqft=lot,
            building_sqft=bldg,
            assessed_value=assessed,
            year_built=year,
            neighborhood=nbhd,
            council_district=str(random.randint(1, 9)),
        )
        session.add(prop)
        properties.append(prop)

    session.commit()
    for p in properties:
        session.refresh(p)
    return properties


def seed_scores(session: Session, properties: list[Property]) -> int:
    """Generate a 'general' score for every property."""
    count = 0
    for prop in properties:
        score = PropertyScore(
            property_id=prop.id,
            scenario="general",
            overall_score=round(random.uniform(25, 95), 1),
            foot_traffic_score=round(random.uniform(10, 100), 1),
            competition_score=round(random.uniform(10, 100), 1),
            safety_score=round(random.uniform(20, 100), 1),
            equity_score=round(random.uniform(15, 100), 1),
            activity_index=round(random.uniform(0.1, 1.0), 3),
        )
        session.add(score)
        count += 1
    session.commit()
    return count


def seed_incidents(session: Session) -> int:
    """Insert 30 incidents spread across Montgomery."""
    count = 0
    for _ in range(30):
        nbhd = random.choice(NEIGHBORHOODS)
        center = NEIGHBORHOOD_COORDS[nbhd]
        inc = Incident(
            incident_id=f"INC-{random.randint(100000, 999999)}",
            incident_type=random.choice(INCIDENT_TYPES),
            latitude=_jitter(center[0], 0.006),
            longitude=_jitter(center[1], 0.006),
            reported_at=_random_dt(180),
            neighborhood=nbhd,
            severity=random.choice(["low", "medium", "high"]),
        )
        session.add(inc)
        count += 1
    session.commit()
    return count


def seed_service_locations(session: Session) -> int:
    """Insert 15 service locations across the city."""
    service_data = [
        ("Winn-Dixie Downtown",    "grocery",  "Downtown"),
        ("Piggly Wiggly Midtown",  "grocery",  "Midtown"),
        ("Publix Dalraida",        "grocery",  "Dalraida"),
        ("ALDI Eastern Blvd",      "grocery",  "Eastern Boulevard Corridor"),
        ("Baptist Medical Center",  "clinic",   "Midtown"),
        ("Family Health Clinic",    "clinic",   "Capitol Heights"),
        ("Montgomery Free Clinic",  "clinic",   "West Montgomery"),
        ("Oak Park",               "park",     "Downtown"),
        ("Lagoon Park",            "park",     "Arrowhead"),
        ("Blount Cultural Park",   "park",     "Woodmere"),
        ("Booker T. Washington HS", "school",  "Capitol Heights"),
        ("Bellingrath Middle",      "school",  "Dalraida"),
        ("Sunshine Daycare",        "daycare", "Cloverdale"),
        ("Little Learners",         "daycare", "Normandale"),
        ("Rosa Parks Library",      "library", "Downtown"),
    ]
    count = 0
    for name, stype, nbhd in service_data:
        center = NEIGHBORHOOD_COORDS[nbhd]
        loc = ServiceLocation(
            name=name,
            service_type=stype,
            latitude=_jitter(center[0], 0.003),
            longitude=_jitter(center[1], 0.003),
            address=f"{random.randint(100, 3000)} {random.choice(STREET_NAMES)}",
            neighborhood=nbhd,
        )
        session.add(loc)
        count += 1
    session.commit()
    return count


def seed_city_projects(session: Session) -> int:
    """Insert 5 city infrastructure projects."""
    projects = [
        {
            "project_name": "Dexter Avenue Streetscape Improvement",
            "project_type": "streetscape",
            "status": "ongoing",
            "nbhd": "Downtown",
            "budget": 4_500_000,
            "description": "Complete streetscape renovation including new sidewalks, lighting, landscaping, and bike lanes along Dexter Ave from the Capitol to Union Station.",
        },
        {
            "project_name": "Capitol Heights Community Center",
            "project_type": "infrastructure",
            "status": "planned",
            "nbhd": "Capitol Heights",
            "budget": 2_200_000,
            "description": "New community center with event space, computer lab, and youth programs.",
        },
        {
            "project_name": "West Montgomery Park Revitalization",
            "project_type": "park",
            "status": "ongoing",
            "nbhd": "West Montgomery",
            "budget": 1_800_000,
            "description": "Renovation of existing park including new playground equipment, walking trails, and a splash pad.",
        },
        {
            "project_name": "Eastern Blvd Transit Hub",
            "project_type": "transit",
            "status": "planned",
            "nbhd": "Eastern Boulevard Corridor",
            "budget": 6_000_000,
            "description": "Multi-modal transit hub with bus rapid transit connections and park-and-ride facilities.",
        },
        {
            "project_name": "Cloverdale Historic Sidewalk Repair",
            "project_type": "infrastructure",
            "status": "completed",
            "nbhd": "Cloverdale",
            "budget": 750_000,
            "description": "ADA-compliant sidewalk repairs and historic brick restoration throughout the Cloverdale neighborhood.",
        },
    ]
    count = 0
    for p in projects:
        center = NEIGHBORHOOD_COORDS[p["nbhd"]]
        cp = CityProject(
            project_name=p["project_name"],
            project_type=p["project_type"],
            status=p["status"],
            latitude=_jitter(center[0], 0.002),
            longitude=_jitter(center[1], 0.002),
            budget=p["budget"],
            description=p["description"],
        )
        session.add(cp)
        count += 1
    session.commit()
    return count


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("  UrbanPulse — Montgomery, AL  Seed Script")
    print("=" * 60)

    # Create tables
    SQLModel.metadata.create_all(engine)
    print(f"\n[+] Database created at: {os.path.abspath(DB_PATH)}")

    with Session(engine) as session:
        # Properties
        properties = seed_properties(session)
        print(f"[+] Seeded {len(properties)} properties")

        # Scores
        n_scores = seed_scores(session, properties)
        print(f"[+] Seeded {n_scores} property scores")

        # Incidents
        n_incidents = seed_incidents(session)
        print(f"[+] Seeded {n_incidents} incidents")

        # Service locations
        n_services = seed_service_locations(session)
        print(f"[+] Seeded {n_services} service locations")

        # City projects
        n_projects = seed_city_projects(session)
        print(f"[+] Seeded {n_projects} city projects")

    print("\n" + "=" * 60)
    print("  Summary")
    print("-" * 60)
    print(f"  Properties:         {len(properties)}")
    print(f"  Property Scores:    {n_scores}")
    print(f"  Incidents:          {n_incidents}")
    print(f"  Service Locations:  {n_services}")
    print(f"  City Projects:      {n_projects}")
    print("=" * 60)
    print("\nDone! You can inspect the database with:")
    print(f"  sqlite3 {os.path.abspath(DB_PATH)}")
    print("  .tables")
    print("  SELECT COUNT(*) FROM properties;")


if __name__ == "__main__":
    main()
