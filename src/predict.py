#!/usr/bin/env python
"""Prédiction unitaire : la fonction que l'API de la semaine 3 appellera.

Usage :
  python src/predict.py "Livraison rapide, très satisfait"
  >>> from predict import predict ; predict("texte")
"""
import sys
from functools import lru_cache
from pathlib import Path
from typing import Literal, Protocol, TypedDict, cast

import joblib

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"


class Prediction(TypedDict):
    label: Literal["positive", "negative"]
    score: float


class ModelPipeline(Protocol):
    classes_: object

    def predict(self, texts: list[str]) -> object: ...

    def predict_proba(self, texts: list[str]) -> object: ...


@lru_cache(maxsize=1)
def charger_modele() -> ModelPipeline:
    """Chargé une seule fois par processus, pas à chaque appel."""
    if not MODELE.exists():
        raise FileNotFoundError("models/sentiment.joblib absent : lancez python src/train.py")
    return cast(ModelPipeline, joblib.load(MODELE))


def predict(texte: str) -> Prediction:
    """Renvoie {'label': 'positive'|'negative', 'score': float}."""
    if not isinstance(texte, str) or not texte.strip():
        raise ValueError("texte vide")
    pipeline = charger_modele()
    etiquette = str(cast(list[str], pipeline.predict([texte]))[0])
    if etiquette not in {"positive", "negative"}:
        raise ValueError("étiquette du modèle inconnue")
    probabilites = cast(list[list[float]], pipeline.predict_proba([texte]))
    score = float(max(probabilites[0]))
    label: Literal["positive", "negative"] = "positive" if etiquette == "positive" else "negative"
    return {"label": label, "score": round(score, 4)}


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    resultat = predict(" ".join(sys.argv[1:]))
    print(f"{resultat['label']} (confiance {resultat['score']:.0%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
