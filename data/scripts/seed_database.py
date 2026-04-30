"""Seed the JSON database with initial data."""
import json
import os
import sys
from pathlib import Path

# Add the backend to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "backend"))

import json
import os
from datetime import datetime
from pathlib import Path

# Add the backend to the path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "backend"))

from backend.app.database import db


def load_json(filename: str) -> list:
    """Load JSON data from seed files."""
    seed_path = Path(__file__).parent.parent / "seed" / filename
    with open(seed_path, encoding="utf-8") as f:
        return json.load(f)


def seed():
    """Seed the JSON database with initial data."""
    print("Seeding JSON database...")

    try:
        # Create a default tenant
        tenant_data = {
            "name": "Demo Tenant",
            "slug": "demo",
            "subscription_plan": "free",
            "max_users": 10,
            "active": True,
        }
        tenant = db.insert("tenants", tenant_data)
        tenant_id = tenant["id"]
        print(f"Created tenant: {tenant['name']}")

        # Create a default user
        from backend.app.application.auth_service import AuthService
        user_data = {
            "tenant_id": tenant_id,
            "email": "admin@demo.com",
            "password_hash": AuthService.hash_password("password123"),
            "first_name": "Admin",
            "last_name": "User",
            "role": "admin",
            "active": True,
        }
        user = db.insert("users", user_data)
        user_id = user["id"]
        print(f"Created user: {user['email']}")

        # Seed exploitations
        exploitations = load_json("exploitations.json")
        exp_map = {}
        for exp in exploitations:
            exp_data = {
                "tenant_id": tenant_id,
                "owner_id": user_id,
                "name": exp["name"],
                "region": exp["location"],
                "main_crops": exp["type"],
                "active": True,
            }
            exploitation = db.insert("exploitations", exp_data)
            exp_map[exp["name"]] = exploitation["id"]
            print(f"Created exploitation: {exp['name']}")

        # Seed parcelles
        parcelles = load_json("parcelles.json")
        parc_map = {}
        for p in parcelles:
            expl_id = exp_map.get(p["exploitation_name"])
            if not expl_id:
                continue
            parc_data = {
                "tenant_id": tenant_id,
                "exploitation_id": expl_id,
                "name": p["code"],
                "area": p["surface_ha"],
                "area_unit": "hectares",
                "crop_type": p["culture"],
                "active": True,
            }
            parcelle = db.insert("parcelles", parc_data)
            parc_map[p["code"]] = parcelle["id"]
            print(f"Created parcelle: {p['code']}")

        # Seed weather data
        weather = load_json("weather_data.json")
        for w in weather:
            parc_id = parc_map.get(w["parcelle_code"])
            if not parc_id:
                continue
            expl_id = None
            for exp_name, exp_id in exp_map.items():
                if any(p["code"] == w["parcelle_code"] and p["exploitation_name"] == exp_name for p in parcelles):
                    expl_id = exp_id
                    break
            if not expl_id:
                continue

            weather_data = {
                "tenant_id": tenant_id,
                "exploitation_id": expl_id,
                "date_observation": w["timestamp"].replace("Z", ""),
                "temperature_avg": w["temperature"],
                "humidity": w["humidity"],
                "source": "seed",
            }
            db.insert("meteo_data", weather_data)

        # Seed soil data
        soil = load_json("soil_data.json")
        for s in soil:
            parc_id = parc_map.get(s["parcelle_code"])
            if not parc_id:
                continue
            expl_id = None
            for exp_name, exp_id in exp_map.items():
                if any(p["code"] == s["parcelle_code"] and p["exploitation_name"] == exp_name for p in parcelles):
                    expl_id = exp_id
                    break
            if not expl_id:
                continue

            soil_data = {
                "tenant_id": tenant_id,
                "parcelle_id": parc_id,
                "exploitation_id": expl_id,
                "date_analyse": s["timestamp"].replace("Z", ""),
                "ph": s["ph"],
                "matiere_organique": s["moisture"],  # Using moisture as organic matter for demo
            }
            db.insert("sol_qualite", soil_data)

        print("JSON database seeded successfully!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        raise


if __name__ == "__main__":
    seed()