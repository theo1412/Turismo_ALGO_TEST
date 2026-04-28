# Vehicle Display Algorithm Demo

Prototype Flask pour tester l'algorithme d'affichage des vehicules selon le pays du site, le pays d'immatriculation, les offres disponibles, les prix et la date de disponibilite.

## Objectif

Le projet simule trois sites pays: France, Belgique et Luxembourg.

Un meme modele peut exister sous plusieurs stocks/variantes:

- immatriculation differente: `FR`, `BE`, `LU`
- type different: `neuf` ou `occasion`
- date de disponibilite differente
- grille d'offres differente: duree, km/mois, prix

Le catalogue public agrege les variantes d'un meme modele via `catalog_id`, puis affiche uniquement les offres eligibles.

## Regles metier

- Les offres sont rattachees au stock du vehicule, pas au site.
- Un vehicule immatricule dans un autre pays que le site consulte ne peut afficher que les offres de 6 mois maximum.
- Pour chaque combinaison `duree + km/mois`, l'algorithme affiche le prix le moins cher parmi les stocks eligibles.
- Le catalogue ne prend en compte que les stocks disponibles dans les 3 prochains mois a partir de la date simulee.
- Une date de disponibilite vide signifie disponible immediatement.
- La meme logique s'applique sur la fiche detail vehicule.

## Lancer en local

```bash
python3 -m pip install -r requirements.txt
python3 -m flask --app app run --port 5002
```

Puis ouvrir:

```text
http://127.0.0.1:5002
```

Interface admin:

```text
http://127.0.0.1:5002/admin
```

## Tester avec ngrok

Dans un premier terminal:

```bash
python3 -m flask --app app run --port 5002
```

Dans un second terminal:

```bash
ngrok http 5002
```

Envoyer l'URL publique ngrok aux testeurs.

## Fonctionnement de l'admin

Dans `/admin`, chaque ligne correspond a un stock.

Champs importants:

- `Reference catalogue`: permet de regrouper plusieurs stocks sous un meme vehicule public.
- `Pays d'immatriculation`: determine la regle locale/etrangere.
- `Type`: `neuf` ou `occasion`.
- `Date de disponibilite`: sert au filtre des 3 prochains mois.
- `Offres disponibles`: grille complete `duree / km par mois / prix`.

Le bouton `+ Variante` permet de creer rapidement le meme vehicule avec une autre immatriculation, un autre type ou une autre grille tarifaire.

## Tester l'algorithme

```bash
behave
```

Les scenarios BDD couvrent:

- restriction des vehicules etrangers a 6 mois
- choix du prix le moins cher par combinaison duree/km
- aggregation de plusieurs stocks d'un meme vehicule
- prise en compte de plusieurs kilometrages
- filtre dynamique selon la date de disponibilite

## API utile

Catalogue:

```text
GET /api/catalog?site=BE&today=2026-04-27
```

Detail vehicule:

```text
GET /api/vehicle/<catalog_id>?site=LU&today=2026-04-27
```

Parametres:

- `site`: `BE`, `FR` ou `LU`
- `today`: date simulee au format `YYYY-MM-DD`

## Deploiement rapide sur Render

Le projet contient un `Procfile`:

```text
web: gunicorn app:app
```

Sur Render:

- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`
- Instance Type: `Free`

Note: sur un hebergement gratuit avec filesystem ephemere, les modifications faites dans `data/vehicles.json` via l'admin peuvent etre perdues au redeploiement. Pour une vraie persistance multi-utilisateur, prevoir une base de donnees.

