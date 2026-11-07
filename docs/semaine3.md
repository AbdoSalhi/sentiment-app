# Semaine 3 : exposer le modèle par une API

## Observations

Vérifications locales effectuées le 7 novembre 2026, avec le modèle de
démonstration réentraîné (290 avis, F1 macro : 0,879).
Les 48 tests passent, dont les six tests de l'API, sans test ignoré.
Un avertissement de dépréciation provenant de Starlette/AnyIO reste sans
conséquence sur les résultats.

Les essais HTTP ont été exécutés contre un vrai serveur Uvicorn local,
arrêté à la fin des vérifications :

| Contrôle | Requête | Résultat observé |
| --- | --- | --- |
| T15 | `GET /health` | 200, `status: OK`, `model: tfidf-logreg (TP2, models/sentiment.joblib)` |
| T16 | `POST /predict`, « Livraison rapide, produit conforme, très satisfait » | 200, `POSITIVE`, score `0.777`, texte renvoyé |
| T17 | `POST /predict`, « Produit cassé et service injoignable, à fuir » | 200, `NEGATIVE`, score `0.7465` |
| T18 | `{"text": ""}`, `{}`, `{"text": 42}` | 422 dans les trois cas, `detail` sous forme de liste |
| Texte blanc | `{"text": "   "}` | 422, `{"detail": "texte vide"}` |
| Texte trop long | 2001 caractères | 422, erreur `string_too_long` |
| Documentation | `GET /docs`, `GET /openapi.json` | 200 |
| T20 | Démarrage avec un chemin de modèle inexistant | `FileNotFoundError`, `Application startup failed`, code de sortie 3 |

Pour T20, un processus séparé a utilisé un chemin inexistant dans `src.predict.MODELE`.
Le véritable fichier du modèle est resté en place. L'essai emprunte le même
chargement de démarrage que l'application normale.

## Pourquoi refuser le démarrage sans modèle plutôt que répondre 503 ?

Le modèle est indispensable pour rendre le service annoncé. Le charger dans
le cycle de démarrage permet de détecter immédiatement une installation
incomplète, avant d'accepter des requêtes. Nous avons observé qu'Uvicorn
signale `FileNotFoundError` puis `Application startup failed` quand le fichier
est absent ; avec le modèle présent, `/health` répond 200 et les prédictions
fonctionnent. Répondre 503 supposerait de maintenir un service démarré mais
indisponible, avec une gestion explicite de cet état. Au TP3, nous choisissons
de refuser le démarrage et de demander l'entraînement préalable.

## Le refus du texte vide par Pydantic et par predict() est-il redondant ?

Les deux validations protègent deux points d'entrée différents. Pydantic
contrôle les requêtes HTTP : champ obligatoire, chaîne de caractères et
longueur comprise entre 1 et 2000. La fonction `predict()` du TP2 peut aussi
être appelée directement en Python ou en ligne de commande ; sa validation
reste donc nécessaire même sans API.

Nous avons observé une différence précise : `""` est refusé par Pydantic,
avec une liste d'erreurs dans `detail`, tandis que `"   "` satisfait la
longueur minimale puis est refusé par `predict()`. L'API traduit alors son
`ValueError("texte vide")` en 422 avec un `detail` textuel. La protection
fonctionne, mais les deux formes d'erreur ne sont pas uniformes ; le guide
prévoit d'améliorer ce contrat au TP4.

## CI et reproduction

La CI installe `requirements-ci.txt`, génère le jeu de démonstration,
entraîne le modèle, puis lance la suite complète. Le modèle et les données
générées restent ignorés par Git ; `models/metrics.json` contient désormais
les mesures du modèle de démonstration utilisé au TP3.

La CI GitHub n'a pas encore été exécutée pour ces changements locaux :
le contrôle T19 reste à vérifier dans l'onglet Actions après le push.
Chaque membre doit également reproduire les essais sur son poste et
commiter son propre travail sous son identité.
