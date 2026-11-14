"""Prédiction indépendante du dépôt et de l'API."""
from functools import lru_cache
from importlib.resources import files
from typing import Any, TypedDict

import joblib


class Resultat(TypedDict):
    label: str
    score: float


@lru_cache(maxsize=1)
def charger_modele() -> Any:
    with files("sentiment_app").joinpath("modele/sentiment.joblib").open("rb") as stream:
        return joblib.load(stream)


def predict(texte: str) -> Resultat:
    if not isinstance(texte, str) or not texte.strip():
        raise ValueError("texte vide")
    modele = charger_modele()
    return {"label": str(modele.predict([texte])[0]),
            "score": round(float(modele.predict_proba([texte]).max()), 4)}
