# Fiche de cadrage : Questions sur le règlement intérieur

## Besoin en une phrase (obligatoire)

Créer un système capable de répondre automatiquement aux questions des étudiants sur le règlement intérieur de leur établissement, en utilisant les documents officiels.

## Utilisateur final (obligatoire)

Les étudiants et le personnel administratif qui souhaitent obtenir rapidement des informations sur les règles de l'établissement.

## Approche retenue (obligatoire)

Cocher une seule case :

- [ ] Règles métier
- [ ] Machine learning
- [x] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)

Nous avons choisi le RAG car (a) nous disposons de documents officiels sans avoir besoin de données étiquetées pour entraîner un modèle. De plus, (b) chaque réponse peut être vérifiée grâce aux passages du règlement utilisés comme sources.

## Données nécessaires et leur origine (obligatoire)

Les données nécessaires sont les documents officiels du règlement intérieur, disponibles auprès de l'administration ou sur le site de l'établissement. Ces documents seront utilisés pour rechercher les informations pertinentes.

## Métrique de succès et seuil d'acceptation (obligatoire)

L'objectif est d'obtenir au moins 90 % de réponses correctes sur un ensemble de 100 questions de test. Chaque réponse doit également citer le passage du règlement qui la justifie.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Une mauvaise réponse pourrait induire un étudiant en erreur sur ses droits ou ses obligations. En cas de doute ou de question importante, l'utilisateur devra confirmer l'information auprès de l'administration.

## Risques éthiques ou de confidentialité (obligatoire)

Le système pourrait fournir des informations incorrectes ou basées sur une ancienne version du règlement. Il faut donc utiliser des documents à jour et éviter de conserver inutilement les données personnelles présentes dans les questions.

## Approche écartée et pourquoi (facultatif)

Le modèle génératif seul a été écarté car il risque d'inventer des règles ou de donner des réponses sans sources vérifiables.