# sentiment-app

Application de classification d'avis français : modèle TF-IDF et régression
logistique, API FastAPI, client web, interface Streamlit et paquet Python.

## Correspondance avec le manuel V1.1

Les anciens énoncés du dépôt utilisent une autre numérotation. Dans le manuel :
Atelier 0 = cadrage/environnement ; TP1 = modèle/API ; TP2 = API protégée/client
web ; TP3 = Streamlit/graphiques ; TP4 = paquet installable.

## Installation sur Windows

Depuis la racine du projet, avec Python 3.11 :

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-ci.txt -r requirements-dev.txt
.\.venv\Scripts\python.exe scripts/configurer.py
.\.venv\Scripts\python.exe src/make_demo.py
.\.venv\Scripts\python.exe src/train.py
```

`scripts/configurer.py` crée deux clés aléatoires dans `.env` sans les afficher.
Il conserve toute configuration existante. Ne jamais publier `.env`.
`requirements-ci.txt` couvre le volume 1 ; `requirements.txt` conserve les
dépendances de tout le semestre. `requirements.lock` décrit l'environnement
volume 1 vérifié le 14 novembre 2026.

## Lancer l'application

Dans deux terminaux, à la racine :

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.main:app --reload
```

```powershell
.\.venv\Scripts\python.exe -m streamlit run ui/app.py --browser.gatherUsageStats false
```

API : http://127.0.0.1:8000/docs ; interface : http://localhost:8501.
La page comporte un avis unitaire et un CSV (colonne `text`), le tableau des
résultats, deux graphiques et un téléchargement. Exemple : `data/avis_exemple.csv`.

## API versionnée

| Route | Accès | Résultat |
| --- | --- | --- |
| GET /health et /v1/health | Public | Santé du modèle |
| POST /v1/predict | Clé client ou admin | label, score, text |
| GET /v1/modele | Clé admin | Métriques et seuil d'abstention |
| POST /predict | Compatibilité publique dépréciée | Prédiction et en-têtes de migration |

Saisir la clé dans le bouton Authorize de `/docs` ou dans l'en-tête `X-API-Key`.
`API_KEYS` contient les couples `clé:client,clé:admin` ; `API_KEY` est la clé
client de Streamlit. Clés d'au moins 16 caractères ; configuration invalide
refusée au démarrage. Sans clés, les routes protégées refusent toute demande.

Les erreurs de `/v1` suivent `{"erreur":{"code":"...","message":"...","champs":[]}}`.
401 = clé absente/refusée ; 403 = rôle refusé ; 422 = entrée invalide ;
503 = modèle indisponible ; 500 = panne interne sans détails sensibles.
Textes de 1 à 2000 caractères, hors textes entièrement blancs.
Sous 0,60 de confiance : `INDETERMINE`, à vérifier par un humain.

## Client HTML et CORS

```powershell
.\.venv\Scripts\python.exe -m http.server 5500 --directory web
```

Ouvrir http://localhost:5500, saisir l'adresse de l'API et la clé client locale.
La clé reste dans le champ de la page, sans stockage persistant.
`CORS_ORIGINS` autorise par défaut localhost et 127.0.0.1 sur le port 5500.
Une page servie sur 5600 est refusée par le navigateur ; curl n'applique pas CORS.

## Vérifications

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m mypy api
.\.venv\Scripts\python.exe -m pytest -q --cov=api --cov-report=term-missing --cov-fail-under=95
node --test web/client.test.mjs
```

Résultat vérifié : 152 passed, 1 skipped, 2 xfailed ; couverture API 100 % ;
12 tests web passent. Le test de paquet est ignoré dans le dépôt puis ses
6 cas sont exécutés dans un environnement isolé par le vérificateur ci-dessous.
Les deux xfail stricts documentent des limites connues du modèle.

## Construire et vérifier le paquet

```powershell
.\.venv\Scripts\python.exe scripts/construire.py
.\.venv\Scripts\python.exe scripts/verifier_livrable.py
```

`dist/` reçoit la roue et la distribution source 1.0.0. Le modèle est embarqué
dans les deux distributions ; il reste ignoré par Git. Le vérificateur crée
un environnement neuf, installe la roue et teste hors des sources. Résultat
attendu : CONFORME, rapport `docs/livrable-tp4.txt`.
Voir `README-PAQUET.md` pour l'API Python et la commande `sentiment`.

## Livraison GitHub

La CI vérifie Python, types, couverture, client web et paquet isolé, puis
conserve les distributions et le rapport comme artefacts de workflow.
Avant publication : relire les changements, commiter sous votre identité,
pousser et attendre la CI verte. Étiqueter ce commit `v1.0.0` et créer une
release contenant les deux fichiers de `dist/` et `docs/livrable-tp4.txt`.
Ne jamais inclure `.env`, `.venv` ou le modèle brut dans le commit.
Le complément Spring Boot du manuel est une activité distincte facultative.

## Limites et comptes rendus

Le modèle de démonstration est appris sur 290 avis synthétiques ; F1 macro
0,879 sur 58 avis de test. La confiance n'est pas calibrée. Ce modèle classe
le sentiment, pas l'urgence. L'ironie, les avis mitigés et les domaines nouveaux
peuvent produire des erreurs. La publication Streamlit Cloud requiert une API
hébergée et joignable ; une API sur localhost ne suffit pas.

Les rapports `docs/semaine2.md` à `docs/semaine5.md` décrivent les anciennes
séances. L'état présent est détaillé dans `docs/verification-manuel-v1.1.md`.

## Membres

| Nom | GitHub |
| --- | --- |
| Taha Boudane | @BdTaha |
| Salhi Abderrahmane | @AbdoSalhi |
| Choukri Said | @Mrsaidchoukri |
