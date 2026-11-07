"""Évalue les vingt avis indépendants sans les utiliser pour entraîner le modèle."""

import csv
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from api.model import SentimentClassifier

JEU_OR = Path(__file__).resolve().parents[1] / "data" / "jeu_or.csv"


def lire_jeu_or() -> list[dict[str, str]]:
    with JEU_OR.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    classifier = SentimentClassifier()
    counts = {"justes": 0, "abstentions": 0, "erreurs": 0, "erreurs_declarees": 0}
    for number, row in enumerate(lire_jeu_or(), 1):
        result = classifier.predict(row["text"])
        if result["label"] == "INDETERMINE":
            counts["abstentions"] += 1
        elif result["label"] == row["attendu"]:
            counts["justes"] += 1
        else:
            counts["erreurs"] += 1
            counts["erreurs_declarees"] += bool(row["erreur_connue"].strip())
        print(f"{number:02d} | attendu={row['attendu']} | prédit={result['label']} | score={result['score']:.4f} | {row['text']}")
    print(counts)


if __name__ == "__main__":
    main()
