# Fiche de cadrage : Priorisation des avis négatifs

## Besoin en une phrase (obligatoire)

Développer un système capable d'identifier et de prioriser automatiquement les avis négatifs des clients afin de traiter rapidement les réclamations les plus importantes.

## Utilisateur final (obligatoire)

Les équipes du service client et les responsables qualité qui analysent les avis et répondent aux réclamations.

## Approche retenue (obligatoire)

Cocher une seule case :

- [ ] Règles métier
- [x] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)

Nous avons choisi le Machine Learning car (a) nous pouvons utiliser des avis clients déjà étiquetés selon leur sentiment pour entraîner un modèle. De plus, (c) le coût par requête reste faible, ce qui permet de traiter un grand nombre d'avis rapidement.

## Données nécessaires et leur origine (obligatoire)

Les données nécessaires sont les avis clients collectés sur le site de l'entreprise ou les plateformes d'évaluation. Chaque avis devra être étiqueté selon son sentiment, positif ou négatif. La priorité opérationnelle sera décidée par le service client.

## Métrique de succès et seuil d'acceptation (obligatoire)

L'objectif est d'obtenir un F1 macro d'au moins 0,85 sur un jeu de test indépendant. Le rappel de la classe négative est suivi séparément ; la mesure du modèle de démonstration est de 0,931. Ce modèle ne détecte pas l'urgence. Sous 0,60 de confiance, l'API renvoie le cas à un humain.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Une erreur pourrait masquer un avis négatif et retarder sa lecture. Les avis négatifs ou incertains seront vérifiés par le service client, qui évalue lui-même l'urgence.

## Risques éthiques ou de confidentialité (obligatoire)

Les avis peuvent contenir des informations personnelles qu'il faut protéger. Le modèle peut aussi présenter des biais dans la classification de certains types de commentaires ou de certaines langues.

## Approche écartée et pourquoi (facultatif)

Les règles métier seules ont été écartées car elles sont trop limitées pour comprendre les différentes formulations et expressions utilisées dans les avis clients.