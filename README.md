# sentiment-app : dépôt du binôme

Application fil rouge du cours *Développement et déploiement d'applications intelligentes*.
Ce dépôt grandit chaque semaine ; la semaine 1 met en place le cadrage et l'environnement.

## Installation (3 commandes)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell : .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Vérifier son installation

```bash
python scripts/check_setup.py    # diagnostic lisible : versions, dossiers, Git
pytest -q                        # mêmes vérifications sous forme de tests
```

La démarche complète de test, étape par étape, est dans `TESTS.md`.

## Structure

```text
sentiment-app/
├── README.md
├── TP1-ENONCE.md    # énoncé du TP de la semaine 1
├── TESTS.md         # démarche à suivre pour le test
├── requirements.txt
├── .gitignore
├── data/            # jeux de données (versionnés par DVC à partir de la semaine 7)
├── models/          # modèles entraînés (jamais dans Git)
├── app/             # dossier réservé du kit TP1
├── api/             # API FastAPI (semaine 3)
├── ui/              # Streamlit (semaine 5)
├── tests/           # pytest (semaine 1 : tests d'environnement)
├── scripts/         # utilitaires (check_setup, nouveau cas de cadrage)
└── docs/cadrage/    # fiches de cadrage du TP1
```

## TP3 : API FastAPI

Depuis la racine du dépôt, avec Python 3.11 et l'environnement activé :

```powershell
python -m pip install -r requirements-ci.txt
python src/make_demo.py
python src/train.py
python -m pytest -q
python -m uvicorn api.main:app --reload
```

`requirements-ci.txt` contient les dépendances nécessaires aux TP1 à TP5 ;
`requirements.txt` couvre tout le semestre. Le modèle reste ignoré par Git et
doit être entraîné sur chaque poste. La CI le réentraîne avant les tests.

Ouvrir [la documentation interactive](http://127.0.0.1:8000/docs).
`GET /health` indique `OK` et le nom du modèle.
`POST /predict` accepte `{"text": "Livraison rapide, très satisfait"}` et
renvoie `label` (`POSITIVE`, `NEGATIVE` ou `INDETERMINE` depuis le TP4),
`score` (entre 0 et 1) et `text`.
Le texte doit être une chaîne de 1 à 2000 caractères. Un texte vide, composé
d'espaces, absent ou numérique est refusé avec le statut 422.
Sans `models/sentiment.joblib`, l'API refuse de démarrer.

Le compte rendu et les observations sont dans [docs/semaine3.md](docs/semaine3.md).

## TP4 : tests approfondis et qualité

Avec l'environnement virtuel activé et le modèle de démonstration entraîné :

```powershell
python -m pip install -r requirements-dev.txt
python -m pre_commit install
python src/courbe_seuil.py
python src/bilan_jeu_or.py
python -m ruff check .
python -m mypy api
python -m pytest -q --cov=api --cov-report=term-missing --cov-fail-under=95
```

Sous 0,60 de confiance, l'API renvoie `INDETERMINE` et conserve le score.
Les textes composés de blancs sont refusés par le schéma, avec la même
forme d'erreur 422 que les autres entrées invalides. Une indisponibilité
après démarrage donne 503 ; une panne de prédiction donne 500.

Les vingt avis indépendants sont dans `data/jeu_or.csv`. Deux erreurs connues
sont conservées en `xfail` strict. Les mesures et justifications sont dans
[docs/semaine4.md](docs/semaine4.md). La CI applique les mêmes contrôles.
Si le dossier temporaire Windows est inaccessible, ajouter
`--basetemp=.pytest_cache/tp4-temp` à la commande pytest.

## TP5 : interface Streamlit

L'interface analyse un avis ou un fichier CSV avec une colonne `text`.
Elle affiche le verdict, la confiance et les abstentions, puis permet de
télécharger les résultats du fichier. Un exemple est fourni dans
`data/avis_exemple.csv`.

Avec l'environnement activé :

```powershell
python -m pip install -r requirements-ci.txt -r requirements-dev.txt
python src/make_demo.py
python src/train.py
```

Dans un premier terminal :

```powershell
python -m uvicorn api.main:app --reload
```

Dans un second terminal, avec le même environnement activé :

```powershell
python -m streamlit run ui/app.py --server.headless true --browser.gatherUsageStats false
```

Ouvrir [l'interface](http://127.0.0.1:8501). Pour une API à une autre adresse,
définir `$env:API_URL = "http://127.0.0.1:8001"` dans le terminal de Streamlit.
Les tests n'exigent aucun serveur lancé :

```powershell
python -m pytest -q --cov=api --cov-report=term-missing --cov-fail-under=95
```

Les observations et les trois réponses du TP5 sont dans
[docs/semaine5.md](docs/semaine5.md).

## Membres du binôme

| Rôle | Nom | Identifiant GitHub | Travail de la semaine 1 |
| --- | --- | --- | --- |
| Membre A | Taha Boudane | @BdTaha | |
| Membre B | Salhi Abderrahmane | @AbdoSalhi | |
| Membre C | Choukri Said | @Mrsaidchoukri | |
