"""Mesure l'exactitude et l'abstention sur le découpage de test du TP2."""

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib
from sklearn.model_selection import train_test_split

from src.train import GRAINE, MODELE, charger


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allocine", action="store_true")
    args = parser.parse_args()
    data, _ = charger(args.allocine)
    _, texts, _, labels = train_test_split(
        data["review"], data["label"], test_size=0.2,
        random_state=GRAINE, stratify=data["label"],
    )
    pipeline = joblib.load(MODELE)
    predictions = pipeline.predict(texts)
    scores = pipeline.predict_proba(texts).max(axis=1)
    print("seuil | répond à | part | exactitude | erreurs | vers un humain")
    for threshold in (0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.90):
        accepted = scores >= threshold
        count = int(accepted.sum())
        errors = int(((predictions != labels) & accepted).sum())
        accuracy = f"{(count - errors) / count:.3f}" if count else "n/a"
        print(f"{threshold:.2f} | {count} | {count / len(texts):.0%} | {accuracy} | {errors} | {len(texts) - count}")


if __name__ == "__main__":
    main()
