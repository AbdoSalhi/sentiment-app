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

`requirements-ci.txt` contient les dépendances nécessaires aux TP1 à TP3 ;
`requirements.txt` couvre tout le semestre. Le modèle reste ignoré par Git et
doit être entraîné sur chaque poste. La CI le réentraîne avant les tests.

Ouvrir [la documentation interactive](http://127.0.0.1:8000/docs).
`GET /health` indique `OK` et le nom du modèle.
`POST /predict` accepte `{"text": "Livraison rapide, très satisfait"}` et
renvoie `label` (`POSITIVE` ou `NEGATIVE`), `score` (entre 0 et 1) et `text`.
Le texte doit être une chaîne de 1 à 2000 caractères. Un texte vide, composé
d'espaces, absent ou numérique est refusé avec le statut 422.
Sans `models/sentiment.joblib`, l'API refuse de démarrer.

Le compte rendu et les observations sont dans [docs/semaine3.md](docs/semaine3.md).

## Membres du binôme

| Rôle | Nom | Identifiant GitHub | Travail de la semaine 1 |
| --- | --- | --- | --- |
| Membre A | Taha Boudane | @BdTaha | |
| Membre B | Salhi Abderrahmane | @AbdoSalhi | |
| Membre C | Choukri Said | @Mrsaidchoukri | |
