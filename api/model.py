"""Adaptation du prédicteur TP2 au contrat HTTP, sans entraînement."""

from src.predict import charger_modele, predict

MODEL_NAME = "tfidf-logreg (TP2, models/sentiment.joblib)"


def load_model():
    """Réutilise le chargement en cache du TP2."""
    return charger_modele()


def predict_sentiment(text: str) -> dict:
    result = predict(text)
    return {"label": result["label"].upper(), "score": result["score"], "text": text}
