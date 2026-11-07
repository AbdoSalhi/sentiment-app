"""Cycle de vie réel, indisponibilité et pannes internes."""

import pytest
from fastapi.testclient import TestClient

import src.predict as predictor
from api.main import app
from api.model import SEUIL_ABSTENTION, SentimentClassifier


@pytest.fixture(autouse=True)
def clear_model_cache():
    predictor.charger_modele.cache_clear()
    yield
    predictor.charger_modele.cache_clear()


def test_cycle_de_vie():
    with TestClient(app) as client:
        assert isinstance(app.state.model, SentimentClassifier)
        assert client.get("/health").status_code == 200
        assert client.post("/predict", json={"text": "Très satisfait"}).status_code == 200
    assert app.state.model is None


def test_demarrage_sans_modele(monkeypatch, tmp_path):
    monkeypatch.setattr(predictor, "MODELE", tmp_path / "absent.joblib")
    with pytest.raises(FileNotFoundError, match="sentiment.joblib absent"), TestClient(app):
        pytest.fail("Le démarrage devait échouer")


def test_modele_retire_503():
    with TestClient(app) as client:
        del app.state.model
        for response in (
            client.get("/health"),
            client.post("/predict", json={"text": "Très satisfait"}),
        ):
            assert response.status_code == 503
            assert response.json() == {"detail": "Modèle indisponible"}


@pytest.mark.parametrize("error", [RuntimeError("secret interne"), ValueError("bug interne")])
def test_panne_interne_500(monkeypatch, error):
    with TestClient(app, raise_server_exceptions=False) as client:
        def fail(text):
            raise error

        monkeypatch.setattr(app.state.model, "predict", fail)
        response = client.post("/predict", json={"text": "Très satisfait"})
        assert response.status_code == 500
        assert response.json() == {"detail": "Erreur interne de prédiction"}
        assert str(error) not in response.text


def test_etiquettes_inconnues(monkeypatch):
    class UnknownModel:
        classes_ = ["negative", "surprise"]

    monkeypatch.setattr("api.model.charger_modele", lambda: UnknownModel())
    with pytest.raises(ValueError, match="incompatibles"), TestClient(app):
        pytest.fail("Un modèle incompatible ne doit pas démarrer")


@pytest.mark.parametrize(
    "score,expected",
    [(SEUIL_ABSTENTION - 0.0001, "INDETERMINE"), (SEUIL_ABSTENTION, "POSITIVE"), (0.95, "POSITIVE")],
)
def test_frontiere_abstention(monkeypatch, score, expected):
    monkeypatch.setattr("api.model.predict", lambda text: {"label": "positive", "score": score})
    with TestClient(app) as client:
        response = client.post("/predict", json={"text": "Avis de contrôle"})
        assert response.status_code == 200
        assert response.json()["label"] == expected
        assert response.json()["score"] == score


def test_mots_inventes():
    with TestClient(app) as client:
        for text in ("xqzvb wlkptr grombu", "zztkvv ppqrxx", "wzqqbx kvvzz"):
            result = client.post("/predict", json={"text": text}).json()
            assert result["label"] == "INDETERMINE"
            assert 0.5 <= result["score"] < SEUIL_ABSTENTION
