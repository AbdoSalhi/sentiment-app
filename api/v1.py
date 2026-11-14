"""Contrat versionné de classification."""
import json
from pathlib import Path
from typing import Annotated, Any, cast

from fastapi import APIRouter, HTTPException, Request, Security

from api.model import MODEL_NAME, SEUIL_ABSTENTION, SentimentClassifier, SentimentPrediction
from api.schemas import HealthResponse, PredictRequest, PredictResponse
from api.securite import Role, administrateur, authentifier

router = APIRouter(prefix="/v1", tags=["v1"])


def modele(request: Request) -> SentimentClassifier:
    instance = getattr(request.app.state, "model", None)
    if instance is None:
        raise HTTPException(503, "Modèle indisponible")
    return cast(SentimentClassifier, instance)


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> dict[str, str]:
    modele(request)
    return {"status": "OK", "model": MODEL_NAME}


@router.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest, request: Request,
            role: Annotated[Role, Security(authentifier)]) -> SentimentPrediction:
    instance = modele(request)
    try:
        return instance.predict(payload.text)
    except Exception:
        raise HTTPException(500, "Erreur interne de prédiction") from None


@router.get("/modele")
def informations(request: Request, role: Annotated[Role, Security(administrateur)]) -> dict[str, Any]:
    modele(request)
    path = Path(__file__).resolve().parents[1] / "models" / "metrics.json"
    try:
        metrics = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise HTTPException(503, "Métriques indisponibles") from None
    return {"model": MODEL_NAME, "seuil_abstention": SEUIL_ABSTENTION, "metrics": metrics}
