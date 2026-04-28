import json
from datetime import date
from pathlib import Path
from typing import List
from .models import Vehicle, Offer, Country, VehicleType


def load_vehicles(path: str | Path) -> List[Vehicle]:
    """Charge la base de données des véhicules depuis un fichier JSON."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    vehicles = []
    for v in data["vehicles"]:
        offers = [
            Offer(
                duration_months=o["duration_months"],
                km_per_month=o["km_per_month"],
                price=float(o["price"]),
            )
            for o in v["offers"]
        ]
        vehicles.append(Vehicle(
            id=v["id"],
            catalog_id=v.get("catalog_id", v["id"]),
            vehicle_type=VehicleType(v["type"]),
            registration_country=Country(v["registration_country"]),
            availability_date=date.fromisoformat(v["availability_date"]) if v.get("availability_date") else None,
            offers=offers,
        ))
    return vehicles
