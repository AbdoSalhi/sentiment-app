# Vérification du manuel V1.1

Vérifications locales du 14 novembre 2026.

## Réalisations

- Historique Git original récupéré depuis AbdoSalhi/sentiment-app : contributions
  existantes d'AbdoSalhi, Taha et TH conservées. Aucune contribution inventée.
- Trois fiches complétées ; cas 3 aligné sur la classification positif/négatif.
- Modèle de démonstration régénéré : 290 avis, 232 apprentissage, 58 test,
  F1 macro 0,879 et rappel négatif 0,931. Modèle non suivi dans Git.
- API versionnée, clés client/admin, erreurs structurées, validation et CORS.
  Ancienne route conservée avec Deprecation et Link.
- Page HTML avec requête authentifiée et messages d'erreur.
- Streamlit utilise /v1 et API_KEY, lit .env, affiche le tableau, les deux
  graphiques, le résumé et le CSV téléchargeable.
- Paquet 1.0.0 : modèle en ressource, fonction predict(), CLI sentiment,
  roue, distribution source et vérification isolée.
- CI étendue aux tests Node et à la construction/vérification du paquet.

## Résultats

- Ruff : aucun problème ; mypy strict : 6 fichiers API sans erreur.
- pip check : aucune dépendance incompatible.
- pytest : 152 passed, 1 skipped, 2 xfailed ; couverture API 100 %.
- Test Streamlit du fichier : deux graphiques présents, résultats et export cohérents.
- Node : 12 tests passent.
- Paquet installé hors des sources : 6 tests passent, rapport CONFORME.

Le test ignoré dans la suite principale concerne seulement le paquet non installé.
Il est obligatoire dans le vérificateur isolé. Les deux échecs attendus du jeu d'or
restent documentés et stricts. Les nombres diffèrent du manuel car ce dépôt
possède des tests supplémentaires issus des séances précédentes.

## Lecture des graphiques

Sur les six avis d'exemple, trois sont positifs, deux négatifs et un est renvoyé
à un humain. La distribution de confiance permet de voir les réponses proches
du seuil de 0,60 ; elle ne prouve ni calibration ni exactitude sur des données
réelles. Les erreurs de requête ne sont pas incluses dans les tranches de confiance.

## Étapes externes restant à valider

La nouvelle version doit être commitée et poussée sous l'identité du membre
qui livre. La CI GitHub sur ce nouveau commit, l'étiquette et la publication
de la release restent à effectuer ; aucun succès distant n'est présumé.
Le contrôle authentifié avec les accès Git existants confirme que la CI du
commit initial 0352f09 est verte. Aucune release n'existe encore. Ce succès
ne valide pas les changements locaux non poussés.
La procédure Streamlit Cloud est décrite dans le manuel, sans hébergement
effectué ici. Le complément Java est facultatif et n'a pas été ajouté.
