"""Contrat JSON de l'API du TP3."""

from typing import Literal

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000, description="Avis à analyser")


class PredictResponse(BaseModel):
    label: Literal["POSITIVE", "NEGATIVE"]
    score: float = Field(ge=0.0, le=1.0)
    text: str


class HealthResponse(BaseModel):
    status: Literal["OK"]
    model: str
