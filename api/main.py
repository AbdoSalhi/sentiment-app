"""Lancer avec : python -m uvicorn api.main:app --reload."""

import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import cast

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.model import MODEL_NAME, SentimentClassifier, SentimentPrediction
from api.schemas import HealthResponse, PredictRequest, PredictResponse
from api.securite import lire_cles
from api.v1 import router

load_dotenv()

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Échouer avant d'accepter des requêtes si le modèle est absent.
    app.state.api_keys = lire_cles(os.environ.get("API_KEYS", ""))
    logger.info("%d clé(s) d'API configurée(s)", len(app.state.api_keys))
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


@app.post("/predict", response_model=PredictResponse, deprecated=True)
def predict_review(payload: PredictRequest, request: Request, response: Response) -> SentimentPrediction:
    response.headers["Deprecation"] = "true"
    response.headers["Link"] = '</v1/predict>; rel="successor-version"'
    model = get_model(request)
    try:
        return model.predict(payload.text)
    except Exception:
        logger.exception("Échec de la prédiction")
        raise HTTPException(status_code=500, detail="Erreur interne de prédiction") from None


app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in os.environ.get(
        "CORS_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500"
    ).split(",") if origin.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)
app.include_router(router)


@app.exception_handler(StarletteHTTPException)
async def erreur_http(request: Request, exc: StarletteHTTPException) -> Response:
    if not request.url.path.startswith("/v1/"):
        return await http_exception_handler(request, exc)
    codes = {401: "NON_AUTHENTIFIE", 403: "ACCES_REFUSE", 404: "INTROUVABLE",
             503: "MODELE_INDISPONIBLE"}
    return JSONResponse(status_code=exc.status_code, content={"erreur": {
        "code": codes.get(exc.status_code, "ERREUR_INTERNE"),
        "message": str(exc.detail), "champs": [],
    }}, headers=exc.headers)


@app.exception_handler(RequestValidationError)
async def erreur_validation(request: Request, exc: RequestValidationError) -> Response:
    if not request.url.path.startswith("/v1/"):
        return await request_validation_exception_handler(request, exc)
    champs = [{"champ": ".".join(str(part) for part in e["loc"]),
               "message": e["msg"]} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"erreur": {
        "code": "ENTREE_INVALIDE", "message": "Entrée refusée par le contrat de l'API",
        "champs": champs,
    }})
