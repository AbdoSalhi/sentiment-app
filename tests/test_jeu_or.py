"""Jeu indépendant : erreurs connues explicites et abstentions comptabilisées."""

import csv
from pathlib import Path

import pytest

from api.model import SentimentClassifier
from src.bilan_jeu_or import lire_jeu_or

ROWS = lire_jeu_or()


def test_jeu_or_complet():
    assert len(ROWS) == 20
    assert all(set(row) == {"text", "attendu", "difficulte", "erreur_connue"} for row in ROWS)
    assert len({row["text"] for row in ROWS}) == 20
    assert all(row["text"].strip() and row["attendu"] in {"POSITIVE", "NEGATIVE"} for row in ROWS)
    assert sum(bool(row["difficulte"].strip()) for row in ROWS) >= 5
    data_path = Path(__file__).resolve().parents[1] / "data" / "demo_reviews.csv"
    with data_path.open(encoding="utf-8", newline="") as stream:
        training_texts = {row["review"].strip().casefold() for row in csv.DictReader(stream)}
    assert not {row["text"].strip().casefold() for row in ROWS} & training_texts


@pytest.fixture(scope="module")
def classifier():
    return SentimentClassifier()


@pytest.mark.parametrize(
    "row",
    [
        pytest.param(
            row,
            id=f"avis-{number:02d}",
            marks=pytest.mark.xfail(strict=True, raises=AssertionError, reason=row["erreur_connue"])
            if row["erreur_connue"].strip() else (),
        )
        for number, row in enumerate(ROWS, 1)
    ],
)
def test_avis(classifier, row):
    result = classifier.predict(row["text"])
    assert result["label"] in {row["attendu"], "INDETERMINE"}


def test_bilan_coherent(classifier):
    labels = [classifier.predict(row["text"])["label"] for row in ROWS]
    abstentions = sum(label == "INDETERMINE" for label in labels)
    correct = sum(label == row["attendu"] for label, row in zip(labels, ROWS, strict=True))
    errors = sum(label not in {row["attendu"], "INDETERMINE"} for label, row in zip(labels, ROWS, strict=True))
    assert correct + abstentions + errors == 20
    assert all(row["erreur_connue"].strip() for label, row in zip(labels, ROWS, strict=True) if label not in {row["attendu"], "INDETERMINE"})
