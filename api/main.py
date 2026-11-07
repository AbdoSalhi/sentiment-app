"""Lancer avec : python -m uvicorn api.main:app --reload."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import cast

from fastapi import FastAPI, HTTPException, Request

from api.model import MODEL_NAME, SentimentClassifier, SentimentPrediction
from api.schemas import HealthResponse, PredictRequest, PredictResponse

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Échouer avant d'accepter des requêtes si le modèle est absent.
    app.state.model = SentimentClassifier()
    logger.info("Modèle chargé avec succès : %s", MODEL_NAME)
    try:
        yield
    finally:
        app.state.model = None


app = FastAPI(title="API de sentiment", version="1.0.0", lifespan=lifespan)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "API de sentiment : documentation sur /docs"}


def get_model(request: Request) -> SentimentClassifier:
    model = getattr(request.app.state, "model", None)
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle indisponible")
    return cast(SentimentClassifier, model)


@app.get("/health", response_model=HealthResponse)
def health(request: Request) -> dict[str, str]:
    get_model(request)
    return {"status": "OK", "model": MODEL_NAME}


@app.post("/predict", response_model=PredictResponse)
def predict_review(payload: PredictRequest, request: Request) -> SentimentPrediction:
    model = get_model(request)
    try:
        return model.predict(payload.text)
    except Exception:
        logger.exception("Échec de la prédiction")
        raise HTTPException(status_code=500, detail="Erreur interne de prédiction") from None
