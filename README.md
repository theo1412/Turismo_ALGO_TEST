# Vehicle Display Algorithm Demo

Flask prototype for testing a vehicle display algorithm based on the website country, vehicle registration country, available offers, pricing, mileage packages, and availability dates.

## Goal

The project simulates three country-specific websites: France, Belgium, and Luxembourg.

The same public vehicle model can exist as multiple stock variants:

- different registration country: `FR`, `BE`, `LU`
- different condition: `neuf` or `occasion`
- different availability date
- different offer grid: duration, km/month, price

The public catalog groups variants of the same model through `catalog_id`, then displays only the eligible offers.

## Business Rules

- Offers belong to a vehicle stock variant, not to a website.
- A vehicle registered in a country different from the visited website can only display offers up to 6 months.
- For each `duration + km/month` combination, the algorithm displays the cheapest eligible price.
- The catalog only considers stock variants available within the next 3 months from the simulated date.
- An empty availability date means the stock is available immediately.
- The same logic applies on the vehicle detail page.

## Run Locally

```bash
python3 -m pip install -r requirements.txt
python3 -m flask --app app run --port 5002
```

Then open:

```text
http://127.0.0.1:5002
```

Admin interface:

```text
http://127.0.0.1:5002/admin
```

## Test With ngrok

In a first terminal:

```bash
python3 -m flask --app app run --port 5002
```

In a second terminal:

```bash
ngrok http 5002
```

Share the public ngrok URL with testers.

## Admin Workflow

In `/admin`, each row represents a stock variant.

Important fields:

- `Reference catalogue`: groups multiple stock variants under the same public vehicle.
- `Pays d'immatriculation`: defines whether the vehicle is local or foreign for a website.
- `Type`: `neuf` or `occasion`.
- `Date de disponibilite`: used by the 3-month availability filter.
- `Offres disponibles`: complete `duration / km per month / price` grid.

The `+ Variante` button quickly creates the same vehicle with another registration country, another condition, or another pricing grid.

## Test the Algorithm

```bash
behave
```

The BDD scenarios cover:

- foreign-registered vehicles limited to 6 months
- cheapest offer selection per duration/km combination
- aggregation of multiple stock variants under one public vehicle
- multiple mileage options
- dynamic filtering by availability date

## Useful API

Catalog:

```text
GET /api/catalog?site=BE&today=2026-04-27
```

Vehicle detail:

```text
GET /api/vehicle/<catalog_id>?site=LU&today=2026-04-27
```

Parameters:

- `site`: `BE`, `FR`, or `LU`
- `today`: simulated date in `YYYY-MM-DD` format

## Quick Render Deployment

The project includes a `Procfile`:

```text
web: gunicorn app:app
```

On Render:

- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`
- Instance Type: `Free`

Note: on free hosting with an ephemeral filesystem, changes made to `data/vehicles.json` through the admin can be lost after redeploys or restarts. For durable multi-user persistence, use a database.

