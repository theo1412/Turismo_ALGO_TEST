from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional


class Country(str, Enum):
    FR = "FR"
    BE = "BE"
    LU = "LU"


class VehicleType(str, Enum):
    NEW = "neuf"
    USED = "occasion"


@dataclass
class Offer:
    duration_months: int
    km_per_month: int
    price: float


@dataclass
class Vehicle:
    id: str
    catalog_id: str
    vehicle_type: VehicleType
    registration_country: Country
    availability_date: Optional[date] = None
    offers: List[Offer] = field(default_factory=list)
