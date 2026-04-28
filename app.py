import json
import os
import sys
import uuid
from collections import defaultdict
from datetime import date
from flask import Flask, jsonify, render_template, request

sys.path.insert(0, os.path.dirname(__file__))
from src.models import Vehicle, Offer, Country, VehicleType
from src.vehicle_display import get_display_offers, add_months

app = Flask(__name__)
DATA = os.path.join(os.path.dirname(__file__), "data", "vehicles.json")


def load():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def save(data):
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def to_models(raw_list):
    result = []
    for v in raw_list:
        offers = [
            Offer(o["duration_months"], o["km_per_month"], float(o["price"]))
            for o in v.get("offers", [])
        ]
        result.append(Vehicle(
            id=v["id"],
            catalog_id=v.get("catalog_id", v["id"]),
            vehicle_type=VehicleType(v["type"]),
            registration_country=Country(v["registration_country"]),
            availability_date=parse_date(v.get("availability_date")),
            offers=offers,
        ))
    return result


def parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError("Date de disponibilité invalide")


def get_current_date_from_request():
    value = request.args.get("today")
    if not value:
        return date.today()
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError("Date du jour invalide")


def group_raw_vehicles(raw_vehicles):
    grouped = defaultdict(list)
    for raw in raw_vehicles:
        grouped[raw.get("catalog_id", raw["id"])].append(raw)
    return grouped


def is_raw_available_in_window(raw_vehicle, current_date):
    availability_date = parse_date(raw_vehicle.get("availability_date"))
    return availability_date is None or availability_date <= add_months(current_date, 3)


def filter_raw_available_in_window(raw_vehicles, current_date):
    return [
        raw for raw in raw_vehicles
        if is_raw_available_in_window(raw, current_date)
    ]


def parse_offers(raw_offers):
    offers = []
    for o in raw_offers:
        try:
            offers.append({
                "duration_months": int(o["duration_months"]),
                "km_per_month": int(o["km_per_month"]),
                "price": float(o["price"]),
            })
        except (KeyError, TypeError, ValueError):
            raise ValueError("Offre invalide (durée, km, prix requis)")
    return offers


def parse_vehicle_payload(body, existing_vehicle=None):
    if existing_vehicle is None:
        for field in ["name", "brand", "type", "registration_country"]:
            if not body.get(field):
                raise ValueError(f"Champ requis : {field}")

    vehicle_id = existing_vehicle["id"] if existing_vehicle else body.get("id") or str(uuid.uuid4())[:8]
    catalog_id = (
        body.get("catalog_id")
        or (existing_vehicle.get("catalog_id") if existing_vehicle else None)
        or body.get("id")
        or vehicle_id
    )

    payload = {
        "id": vehicle_id,
        "catalog_id": catalog_id,
        "name": body.get("name", existing_vehicle.get("name") if existing_vehicle else ""),
        "brand": body.get("brand", existing_vehicle.get("brand") if existing_vehicle else ""),
        "power_cv": body.get("power_cv", existing_vehicle.get("power_cv") if existing_vehicle else None) or None,
        "category": body.get("category", existing_vehicle.get("category") if existing_vehicle else ""),
        "type": body.get("type", existing_vehicle.get("type") if existing_vehicle else ""),
        "registration_country": body.get(
            "registration_country",
            existing_vehicle.get("registration_country") if existing_vehicle else "",
        ),
        "availability_date": body.get(
            "availability_date",
            existing_vehicle.get("availability_date") if existing_vehicle else "",
        ),
        "image_url": body.get("image_url", existing_vehicle.get("image_url") if existing_vehicle else ""),
        "offers": existing_vehicle.get("offers", []) if existing_vehicle else [],
    }

    if payload["availability_date"]:
        parse_date(payload["availability_date"])

    if "offers" in body:
        payload["offers"] = parse_offers(body["offers"])

    return payload


def build_catalog_entry(raw_group, site_country, current_date):
    models = to_models(raw_group)
    offers = get_display_offers(models, site_country, current_date)
    if not offers:
        return None

    display_group = filter_raw_available_in_window(raw_group, current_date)
    first = display_group[0]
    registration_countries = sorted({raw["registration_country"] for raw in display_group})
    type_labels = sorted({raw["type"] for raw in display_group})
    winning_offer = min(offers, key=lambda offer: offer.price)

    return {
        "id": first.get("catalog_id", first["id"]),
        "name": first.get("name", first["id"]),
        "brand": first.get("brand", ""),
        "power_cv": first.get("power_cv"),
        "category": first.get("category", ""),
        "type": winning_offer.vehicle_type,
        "type_labels": type_labels,
        "registration_country": registration_countries[0] if len(registration_countries) == 1 else "MULTI",
        "registration_countries": registration_countries,
        "availability_dates": sorted({
            raw.get("availability_date") or "disponible"
            for raw in display_group
        }),
        "image_url": first.get("image_url", ""),
        "min_price": min(o.price for o in offers),
        "nb_durations": len({o.duration_months for o in offers}),
        "variant_count": len(raw_group),
    }


# ─── Pages ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("catalog.html")


@app.route("/vehicle/<vid>")
def vehicle_page(vid):
    return render_template("detail.html", vehicle_id=vid)


@app.route("/admin")
def admin():
    return render_template("admin.html")


# ─── Catalog API ─────────────────────────────────────────────────────────────

@app.route("/api/catalog")
def api_catalog():
    site = request.args.get("site", "BE").upper()
    try:
        sc = Country(site)
    except ValueError:
        return jsonify({"error": "Site invalide"}), 400
    try:
        current_date = get_current_date_from_request()
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    data = load()
    result = []
    for raw_group in group_raw_vehicles(data["vehicles"]).values():
        entry = build_catalog_entry(raw_group, sc, current_date)
        if entry:
            result.append(entry)
    result.sort(key=lambda item: (item["min_price"], item["name"].lower()))
    return jsonify(result)


# ─── Vehicle detail API ───────────────────────────────────────────────────────

@app.route("/api/vehicle/<vid>")
def api_vehicle(vid):
    site = request.args.get("site", "BE").upper()
    try:
        sc = Country(site)
    except ValueError:
        return jsonify({"error": "Site invalide"}), 400
    try:
        current_date = get_current_date_from_request()
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    data = load()
    matching = [
        raw for raw in data["vehicles"]
        if raw.get("catalog_id", raw["id"]) == vid or raw["id"] == vid
    ]
    if not matching:
        return jsonify({"error": "Véhicule introuvable"}), 404

    visible_matching = filter_raw_available_in_window(matching, current_date)
    offers = get_display_offers(to_models(matching), sc, current_date)
    first = visible_matching[0] if visible_matching else matching[0]
    return jsonify({
        "id": first.get("catalog_id", first["id"]),
        "name": first.get("name", first["id"]),
        "brand": first.get("brand", ""),
        "power_cv": first.get("power_cv"),
        "category": first.get("category", ""),
        "type": first["type"],
        "registration_country": first["registration_country"],
        "registration_countries": sorted({raw["registration_country"] for raw in visible_matching}),
        "availability_dates": sorted({
            raw.get("availability_date") or "disponible"
            for raw in visible_matching
        }),
        "image_url": first.get("image_url", ""),
        "variant_count": len(visible_matching),
        "offers": [
            {
                "duration_months":      o.duration_months,
                "km_per_month":         o.km_per_month,
                "price":                o.price,
                "vehicle_type":         o.vehicle_type,
                "registration_country": o.registration_country.value,
            }
            for o in offers
        ],
    })


# ─── Admin : véhicules ────────────────────────────────────────────────────────

@app.route("/api/admin/vehicles", methods=["GET"])
def admin_list():
    return jsonify(load()["vehicles"])


@app.route("/api/admin/vehicles", methods=["POST"])
def admin_create():
    b = request.json
    try:
        new_v = parse_vehicle_payload(b)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    data = load()
    if any(v["id"] == new_v["id"] for v in data["vehicles"]):
        return jsonify({"error": "ID stock déjà utilisé"}), 400
    data["vehicles"].append(new_v)
    save(data)
    return jsonify(new_v), 201


@app.route("/api/admin/vehicles/<vid>", methods=["PUT"])
def admin_update(vid):
    data = load()
    v = next((x for x in data["vehicles"] if x["id"] == vid), None)
    if not v:
        return jsonify({"error": "Introuvable"}), 404

    b = request.json
    try:
        updated = parse_vehicle_payload(b, existing_vehicle=v)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    v.update(updated)

    save(data)
    return jsonify(v)


@app.route("/api/admin/vehicles/<vid>", methods=["DELETE"])
def admin_delete(vid):
    data = load()
    before = len(data["vehicles"])
    data["vehicles"] = [x for x in data["vehicles"] if x["id"] != vid]
    if len(data["vehicles"]) == before:
        return jsonify({"error": "Introuvable"}), 404
    save(data)
    return jsonify({"ok": True})


# ─── Admin : offres individuelles (suppression) ───────────────────────────────

@app.route("/api/admin/vehicles/<vid>/offers/<int:idx>", methods=["DELETE"])
def admin_delete_offer(vid, idx):
    data = load()
    v = next((x for x in data["vehicles"] if x["id"] == vid), None)
    if not v:
        return jsonify({"error": "Introuvable"}), 404
    if idx >= len(v["offers"]):
        return jsonify({"error": "Offre introuvable"}), 404
    v["offers"].pop(idx)
    save(data)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
