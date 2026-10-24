# Fiche de cadrage : Ordonnances incomplètes en pharmacie

## Besoin en une phrase (obligatoire)

Détecter automatiquement les ordonnances incomplètes afin d'aider les pharmaciens à identifier les informations manquantes avant de délivrer les médicaments.

## Utilisateur final (obligatoire)

Les pharmaciens et les préparateurs en pharmacie qui vérifient les ordonnances des patients.

## Approche retenue (obligatoire)

Cocher une seule case :

- [x] Règles métier
- [ ] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)

Nous avons choisi les règles métier car (b) chaque anomalie détectée peut être facilement vérifiée par un pharmacien et (c) le coût par requête est faible. De plus, (d) une erreur pourrait avoir des conséquences importantes sur la santé du patient, donc il vaut mieux utiliser des règles précises et contrôlables.

## Données nécessaires et leur origine (obligatoire)

Les données nécessaires sont les informations présentes sur les ordonnances, comme le nom du patient, la date, les médicaments et les posologies. Elles proviennent des ordonnances reçues par la pharmacie, avec un accès autorisé et sécurisé.

## Métrique de succès et seuil d'acceptation (obligatoire)

L'objectif est de détecter au moins 98 % des ordonnances présentant des informations obligatoires manquantes, sur un jeu de test représentatif. Le taux de fausses alertes doit rester inférieur à 5 %.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Une erreur pourrait laisser passer une ordonnance incomplète et mettre en danger le patient. Le pharmacien doit donc vérifier les alertes et valider chaque ordonnance avant la délivrance des médicaments.

## Risques éthiques ou de confidentialité (obligatoire)

Les ordonnances contiennent des données personnelles et médicales sensibles. Il faut protéger ces informations en limitant les accès et en sécurisant leur stockage.

## Approche écartée et pourquoi (facultatif)

Le modèle génératif seul a été écarté car il peut produire des réponses incorrectes ou inventer des informations, ce qui représente un risque dans le domaine médical.