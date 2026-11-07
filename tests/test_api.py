"""Six contrôles du TP3, exécutés avec le vrai modèle TP2."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import app

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"


@pytest.fixture(scope="module")
def client():
    if not MODELE.exists():
        pytest.skip("Modèle absent : lancez python src/make_demo.py puis python src/train.py")
    with TestClient(app) as session:
        yield session


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "/docs" in response.json()["message"]


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "model": "tfidf-logreg (TP2, models/sentiment.joblib)",
    }


def test_predict_positif(client):
    text = "Livraison rapide, produit conforme, très satisfait"
    response = client.post("/predict", json={"text": text})
    assert response.status_code == 200
    result = response.json()
    assert result["label"] == "POSITIVE"
    assert 0.5 <= result["score"] <= 1.0
    assert result["text"] == text


def test_predict_negatif(client):
    response = client.post("/predict", json={"text": "Produit cassé et service injoignable, à fuir"})
    assert response.status_code == 200
    assert response.json()["label"] == "NEGATIVE"
    assert 0.5 <= response.json()["score"] <= 1.0


def test_predict_texte_vide_422(client):
    for text in ("", "   "):
        response = client.post("/predict", json={"text": text})
        assert response.status_code == 422
        assert "detail" in response.json()


def test_predict_champ_manquant_422(client):
    for payload in ({}, {"text": 42}):
        response = client.post("/predict", json=payload)
        assert response.status_code == 422
        assert isinstance(response.json()["detail"], list)
