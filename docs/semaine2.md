Sur les 58 avis du jeu de test, le modèle a commis 7 erreurs : 2 avis négatifs ont été classés positifs et 5 avis positifs ont été classés négatifs, notamment dans des situations où les avis présentent des opinions mitigées.

Ces erreurs s'expliquent par les limites de l'approche TF-IDF associée à la régression logistique, qui prend en compte les mots présents dans le texte sans comprendre pleinement leur contexte, les négations ou les changements de sens.

Pour améliorer les performances, nous pourrions utiliser des n-grammes afin de mieux représenter les expressions, ou expérimenter avec un modèle de langage contextualisé comme CamemBERT.