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
    availability_date: date | None = None
    vehicle_id: str = ""


@dataclass
class CandidateOffer:
    duration_months: int
    km_per_month: int
    price: float
    vehicle_type: str
    registration_country: Country
    availability_date: date | None
    vehicle_id: str


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


def availability_sort_date(availability_date: date | None) -> date:
    return availability_date or date.min


def is_immediately_available(candidate: CandidateOffer, current_date: date | None) -> bool:
    return current_date is None or candidate.availability_date is None or candidate.availability_date <= current_date


def is_available_within_one_month(candidate: CandidateOffer, current_date: date | None) -> bool:
    if current_date is None:
        return True
    if candidate.availability_date is None:
        return True
    return candidate.availability_date <= add_months(current_date, 1)


def choose_candidate(
    candidates: List[CandidateOffer],
    site_country: Country,
    current_date: date | None,
) -> CandidateOffer:
    immediate = [
        candidate for candidate in candidates
        if is_immediately_available(candidate, current_date)
    ]
    if immediate:
        return min(
            immediate,
            key=lambda candidate: (
                candidate.price,
                candidate.registration_country != site_country,
                availability_sort_date(candidate.availability_date),
            ),
        )

    within_one_month = [
        candidate for candidate in candidates
        if is_available_within_one_month(candidate, current_date)
    ]
    if len(within_one_month) >= 2:
        return min(
            within_one_month,
            key=lambda candidate: (
                candidate.price,
                candidate.registration_country != site_country,
                availability_sort_date(candidate.availability_date),
            ),
        )

    return min(
        candidates,
        key=lambda candidate: (
            availability_sort_date(candidate.availability_date),
            candidate.price,
            candidate.registration_country != site_country,
        ),
    )


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
    - Pour chaque (durée, km/mois), on choisit le véhicule selon la priorité de disponibilité.
    - Résultat trié par durée croissante, puis km/mois croissant.
    """
    candidates: Dict[Tuple[int, int], List[CandidateOffer]] = {}

    for vehicle in vehicles:
        if not is_available_in_window(vehicle, current_date):
            continue
        is_foreign = vehicle.registration_country != site_country
        for offer in vehicle.offers:
            if is_foreign and offer.duration_months > MAX_FOREIGN_DURATION:
                continue
            key = (offer.duration_months, offer.km_per_month)
            candidates.setdefault(key, []).append(
                CandidateOffer(
                    duration_months=offer.duration_months,
                    km_per_month=offer.km_per_month,
                    price=offer.price,
                    vehicle_type=vehicle.vehicle_type.value,
                    registration_country=vehicle.registration_country,
                    availability_date=vehicle.availability_date,
                    vehicle_id=vehicle.id,
                )
            )

    result = []
    for (duration, km), candidate_list in sorted(candidates.items()):
        selected = choose_candidate(candidate_list, site_country, current_date)
        result.append(DisplayOffer(
            duration_months=duration,
            km_per_month=km,
            price=selected.price,
            vehicle_type=selected.vehicle_type,
            registration_country=selected.registration_country,
            availability_date=selected.availability_date,
            vehicle_id=selected.vehicle_id,
        ))

    return result
