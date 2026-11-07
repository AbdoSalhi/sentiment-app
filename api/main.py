"""Lancer avec : python -m uvicorn api.main:app --reload."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from api.model import MODEL_NAME, load_model, predict_sentiment
from api.schemas import HealthResponse, PredictRequest, PredictResponse

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Échouer avant d'accepter des requêtes si le modèle est absent.
    load_model()
    logger.info("Modèle chargé avec succès : %s", MODEL_NAME)
    yield


app = FastAPI(title="API de sentiment", version="1.0.0", lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "API de sentiment : documentation sur /docs"}


@app.get("/health", response_model=HealthResponse)
def health():
    return {"status": "OK", "model": MODEL_NAME}


@app.post("/predict", response_model=PredictResponse)
def predict_review(payload: PredictRequest):
    try:
        return predict_sentiment(payload.text)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
