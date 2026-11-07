# Semaine 4 : tests approfondis et qualité

## 1. Mesures de départ

Les mesures ont été prises sur l'API du TP3 avant les corrections :

- Les six tests API passent ; la couverture de cette API initiale est de 100 %
  (42 instructions). Ce chiffre ne vérifie pas encore le modèle retiré de
  l'état de l'application, les pannes internes ou les étiquettes incompatibles.
- Ruff signale neuf problèmes : imports à ordonner dans le notebook TP2 et
  le nouveau test des limites, import inutilisé dans `evaluate.py`, deux
  `zip()` sans `strict`, trois variables `l` ambiguës dans les tests TP1.
- Mypy en mode strict signale neuf erreurs dans trois fichiers : fonctions
  non annotées, retours `dict` sans types et appel d'une fonction non typée.
- Les nouveaux tests des limites donnent **2 failed, 9 passed**. Les espaces
  seuls produisent `detail: "texte vide"` au lieu d'une liste d'erreurs.
  Hypothesis réduit aussi le défaut au contre-exemple `texte='\x85'`.

Ces résultats proviennent de ce dépôt, dont l'API TP3 diffère du kit de
référence ; les chiffres du corrigé ne sont pas utilisés comme mesures.

## 2. Contrat d'entrée et défaut corrigé

`tests/test_limites.py` vérifie huit cas paramétrés (vide, espaces, un
caractère, 2000 et 2001 caractères, champ absent, nombre, `null`), un corps
non JSON et deux propriétés Hypothesis. Les propriétés portent sur les
textes Unicode non blancs et les suites de blancs, dont `\x85` et les espaces
insécables. Elles vérifient aussi les étiquettes et les scores renvoyés.

Le `field_validator` de `PredictRequest` refuse maintenant tout texte pour
lequel `text.strip()` est vide. Il conserve le texte original lorsqu'il est
valide. La limite de 2000 caractères porte donc sur le texte reçu.
Tous les refus d'entrée ont désormais un `detail` en liste ; les erreurs de
champ indiquent `loc: ["body", "text"]`. Le modèle du TP2 n'a pas été utilisé
pour corriger ce défaut HTTP. Les onze tests des limites passent trois fois
de suite.

## 3. Seuil d'abstention mesuré

Commande : `python src/courbe_seuil.py`. Même jeu de démonstration et même
découpage que le TP2 : 232 avis d'entraînement et 58 avis de test, graine 42.

| Seuil | Réponses | Part | Exactitude des réponses | Erreurs | Vers un humain |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0,50 | 58 | 100 % | 0,879 | 7 | 0 |
| 0,55 | 47 | 81 % | 0,915 | 4 | 11 |
| 0,60 | 42 | 72 % | 0,952 | 2 | 16 |
| 0,65 | 41 | 71 % | 0,976 | 1 | 17 |
| 0,70 | 37 | 64 % | 1,000 | 0 | 21 |
| 0,75 | 29 | 50 % | 1,000 | 0 | 29 |
| 0,80 | 13 | 22 % | 1,000 | 0 | 45 |
| 0,90 | 0 | 0 % | non définie | 0 | 58 |

Nous retenons `SEUIL_ABSTENTION = 0.60`, le point de départ du guide :
l'exactitude des avis acceptés augmente de 87,9 % à 95,2 %, avec encore
72 % des avis traités automatiquement. Monter à 0,70 supprime les erreurs
sur ces 58 avis, mais transfère 21 avis à un humain au lieu de 16. Ce petit
jeu ne prouve pas l'absence d'erreurs en production ; la confiance du modèle
n'est pas une garantie d'exactitude.

En dessous du seuil, `SentimentClassifier.predict()` renvoie `INDETERMINE`
avec le score original. Au seuil exact, il conserve la polarité. Trois suites
de mots inventés sont vérifiées par les tests : sans vocabulaire connu,
elles reçoivent `INDETERMINE`, avec un score inférieur à 0,60.

## 4. Jeu d'or indépendant

`data/jeu_or.csv` reprend les vingt avis fournis, avec leurs étiquettes et
difficultés. Aucun texte n'est présent dans le jeu de démonstration.
Il comprend dix positifs, dix négatifs et seize cas difficiles : négation,
ironie, avis mitigés ou autres domaines. Les textes et les étiquettes
attendues sont conservés. Seules deux cellules `erreur_connue` ont été
complétées après mesure, sans réentraîner le modèle sur ces avis.

Commande : `python src/bilan_jeu_or.py`.

| Résultat au seuil 0,60 | Nombre |
| --- | ---: |
| Réponses justes | 8 |
| Abstentions | 10 |
| Erreurs franches | 2 |
| Erreurs franches déclarées | 2 |

Le modèle répond donc à 10 avis sur 20, dont 8 correctement. Les dix
abstentions ne sont pas comptées comme réponses justes. Les deux erreurs :

- Avis 8, restaurant : attendu `NEGATIVE`, obtenu `POSITIVE`, score 0,6535.
  La décoration positive domine les critiques des plats ; c'est aussi un
  domaine différent des avis commerciaux de démonstration.
- Avis 20, prix et matériaux : attendu `NEGATIVE`, obtenu `POSITIVE`, score
  0,6359. Le prix raisonnable domine la critique de la qualité du produit.

Ces deux cas restent dans les tests avec `xfail(strict=True,
raises=AssertionError)` et une raison précise. Une amélioration du modèle
qui les résout donnera un `XPASS` strict, donc un échec invitant à retirer
la déclaration d'erreur connue. Les autres pannes ne sont pas masquées par
ces marques.

## 5. Intégration, types et qualité

`tests/test_integration.py` utilise le vrai cycle de vie `with TestClient(app)` :

- Le modèle est chargé au démarrage dans `app.state.model` et libéré de cet
  état à la fermeture.
- Un chemin de modèle absent, avec cache vidé, provoque `FileNotFoundError`
  avant le service des requêtes.
- Un modèle retiré de `app.state` donne 503 sur `/health` et `/predict`.
- Une panne `RuntimeError` ou `ValueError("bug interne")` donne 500 avec un
  message générique. Le détail est journalisé côté serveur et n'est pas
  envoyé au client. La conversion générale de `ValueError` en 422 du TP3
  a été retirée : le schéma traite les erreurs d'entrée avant la prédiction.
- Un modèle aux étiquettes incompatibles refuse de démarrer.
- Les valeurs juste sous le seuil, exactement au seuil et au-dessus du
  seuil vérifient le contrat de l'abstention.

Le retour de `src.predict.predict()` est un `TypedDict` à étiquettes
minuscules explicites. Celui de `SentimentClassifier.predict()` utilise
`Literal["POSITIVE", "NEGATIVE", "INDETERMINE"]`. Une correspondance
explicite remplace `.upper()` et les classes sont vérifiées au démarrage.
Le chargement en cache du TP2 est conservé.

Ruff a corrigé les imports ; les deux `zip()` utilisent `strict=True` et
les variables ambiguës des tests TP1 s'appellent `ligne`. Ces retouches ne
changent aucune assertion des tests fournis. Les deux imports du notebook
TP2 ont seulement été remis en forme.

Résultats finaux locaux :

- `ruff check .` : aucun problème.
- `mypy api` en mode strict : aucun problème dans les quatre fichiers API.
- Suite complète : **89 passed, 2 xfailed**.
- Couverture API : **100 %**, 75 instructions, aucune exclusion ajoutée ;
  le seuil de 95 % est appliqué localement et dans la CI.
- Un avertissement de dépréciation Starlette/AnyIO reste sans conséquence.

Sur ce poste Windows, le répertoire temporaire par défaut de pytest n'était
pas accessible. Le contrôle complet a utilisé
`--basetemp=.pytest_cache/tp4-temp`, sans modifier ni ignorer de test.

## 6. Crochet et CI

Le crochet local exécute Ruff et mypy. Il s'installe dans chaque clone avec
`python -m pre_commit install`, après activation de l'environnement et
installation de `requirements-dev.txt`. Un import `os` inutilisé a été
ajouté provisoirement à `courbe_seuil.py` : le crochet refuse le commit.
L'import a ensuite été retiré et aucun commit fautif n'a été créé.

La CI génère les données et entraîne le modèle, installe les outils TP4,
puis exécute Ruff, mypy et pytest avec le seuil de couverture de 95 %.
Le jeu d'or est versionné ; le modèle, les données générées et les caches
restent ignorés. Le résultat distant est à vérifier après le push.
