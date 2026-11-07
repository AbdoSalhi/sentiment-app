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
