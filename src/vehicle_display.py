import calendar
from datetime import date
from typing import List, Dict, Tuple
from dataclasses import dataclass
from .models import Vehicle, Country

MAX_FOREIGN_DURATION = 6  # mois max pour un véhicule étranger
AVAILABILITY_WINDOW_MONTHS = 3


@dataclass
class DisplayOffer:
    duration_months: int
    km_per_month: int
    price: float
    vehicle_type: str
    registration_country: Country


def add_months(value: date, months: int) -> date:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def is_available_in_window(vehicle: Vehicle, current_date: date | None) -> bool:
    if current_date is None or vehicle.availability_date is None:
        return True
    return vehicle.availability_date <= add_months(current_date, AVAILABILITY_WINDOW_MONTHS)


def get_display_offers(
    vehicles: List[Vehicle],
    site_country: Country,
    current_date: date | None = None,
) -> List[DisplayOffer]:
    """
    Pour un site pays donné, retourne les offres à afficher.

    Règles :
    - Si une date du jour est fournie, seuls les véhicules disponibles dans les 3 prochains mois sont pris en compte.
    - Un véhicule immatriculé dans un autre pays que le site est limité à 6 mois max.
    - Les offres sont liées au pays d'immatriculation (pas au site).
    - Pour chaque (durée, km/mois), on affiche le prix le moins cher parmi les véhicules éligibles.
    - Résultat trié par durée croissante, puis km/mois croissant.
    """
    candidates: Dict[Tuple[int, int], List[Tuple[float, str, Country]]] = {}

    for vehicle in vehicles:
        if not is_available_in_window(vehicle, current_date):
            continue
        is_foreign = vehicle.registration_country != site_country
        for offer in vehicle.offers:
            if is_foreign and offer.duration_months > MAX_FOREIGN_DURATION:
                continue
            key = (offer.duration_months, offer.km_per_month)
            candidates.setdefault(key, []).append(
                (offer.price, vehicle.vehicle_type.value, vehicle.registration_country)
            )

    result = []
    for (duration, km), price_list in sorted(candidates.items()):
        price, vtype, country = min(price_list, key=lambda x: x[0])
        result.append(DisplayOffer(
            duration_months=duration,
            km_per_month=km,
            price=price,
            vehicle_type=vtype,
            registration_country=country,
        ))

    return result
