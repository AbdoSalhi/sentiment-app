"""Contrat typé et abstention autour du prédicteur TP2."""

from typing import Literal, TypedDict, cast

from src.predict import charger_modele, predict

MODEL_NAME = "tfidf-logreg (TP2, models/sentiment.joblib)"
SEUIL_ABSTENTION = 0.60
Label = Literal["POSITIVE", "NEGATIVE", "INDETERMINE"]
ETIQUETTES: dict[str, Label] = {"positive": "POSITIVE", "negative": "NEGATIVE"}


class SentimentPrediction(TypedDict):
    label: Label
    score: float
    text: str


class SentimentClassifier:
    def __init__(self) -> None:
        pipeline = charger_modele()
        classes = {str(label) for label in cast(list[str], pipeline.classes_)}
        if classes != set(ETIQUETTES):
            raise ValueError(f"Étiquettes du modèle incompatibles : {sorted(classes)}")

    def predict(self, text: str) -> SentimentPrediction:
        result = predict(text)
        label = ETIQUETTES[result["label"]]
        if result["score"] < SEUIL_ABSTENTION:
            label = "INDETERMINE"
        return {"label": label, "score": result["score"], "text": text}
