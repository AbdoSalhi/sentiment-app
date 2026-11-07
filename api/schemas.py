"""Contrat JSON et validation des textes Unicode."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PredictRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000, description="Avis à analyser")

    @field_validator("text")
    @classmethod
    def refuser_les_blancs(cls, text: str) -> str:
        if not text.strip():
            raise ValueError("texte vide")
        return text


class PredictResponse(BaseModel):
    label: Literal["POSITIVE", "NEGATIVE", "INDETERMINE"]
    score: float = Field(ge=0.0, le=1.0)
    text: str


class HealthResponse(BaseModel):
    status: Literal["OK"]
    model: str
