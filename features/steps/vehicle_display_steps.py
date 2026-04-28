import sys
import os
from datetime import date
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from behave import given, when, then
from src.models import Vehicle, Offer, Country, VehicleType
from src.vehicle_display import get_display_offers


# ─── Setup ───────────────────────────────────────────────────────────────────

@given("la base de données contient les véhicules suivants :")
@given("la base de données contient les véhicules suivants ")
@given("que la base de données contient les véhicules suivants :")
@given("que la base de données contient les véhicules suivants ")
def step_load_vehicles(context):
    context.vehicles = {}
    for row in context.table:
        catalog_id = row["catalogue"] if "catalogue" in row.headings else row["id"]
        availability_date = (
            date.fromisoformat(row["disponible_le"])
            if "disponible_le" in row.headings and row["disponible_le"]
            else None
        )
        context.vehicles[row["id"]] = Vehicle(
            id=row["id"],
            catalog_id=catalog_id,
            vehicle_type=VehicleType(row["type"]),
            registration_country=Country(row["immatriculation"]),
            availability_date=availability_date,
        )


@given("la base de données contient les offres suivantes :")
@given("la base de données contient les offres suivantes ")
@given("que la base de données contient les offres suivantes :")
@given("que la base de données contient les offres suivantes ")
def step_load_offers(context):
    for row in context.table:
        offer = Offer(
            duration_months=int(row["duree_mois"]),
            km_per_month=int(row["km_mois"]),
            price=float(row["prix"]),
        )
        context.vehicles[row["vehicule"]].offers.append(offer)


# ─── Action ──────────────────────────────────────────────────────────────────

@given("je suis sur le site {country}")
@given("que je suis sur le site {country}")
def step_set_site(context, country):
    context.site_country = Country(country)


@given("nous sommes le {current_date}")
@given("que nous sommes le {current_date}")
def step_set_current_date(context, current_date):
    context.current_date = date.fromisoformat(current_date)


@when("je consulte le catalogue de véhicules")
def step_view_catalog(context):
    context.display_offers = get_display_offers(
        list(context.vehicles.values()),
        context.site_country,
        getattr(context, "current_date", None),
    )


# ─── Assertions ──────────────────────────────────────────────────────────────

@then("je dois voir les offres suivantes :")
@then("je dois voir les offres suivantes ")
def step_check_offers(context):
    expected = [
        {
            "duree_mois": int(row["duree_mois"]),
            "km_mois":    int(row["km_mois"]),
            "prix":       float(row["prix"]),
            "immat":      row["immatriculation"],
            "type":       row["type"],
        }
        for row in context.table
    ]

    actual = [
        {
            "duree_mois": o.duration_months,
            "km_mois":    o.km_per_month,
            "prix":       o.price,
            "immat":      o.registration_country.value,
            "type":       o.vehicle_type,
        }
        for o in context.display_offers
    ]

    assert actual == expected, (
        f"\nSite : {context.site_country}\n"
        f"Attendu  : {expected}\n"
        f"Obtenu   : {actual}"
    )


@then("je ne dois voir aucune offre")
def step_no_offers(context):
    assert context.display_offers == [], (
        f"Attendu : aucune offre, obtenu : {context.display_offers}"
    )
