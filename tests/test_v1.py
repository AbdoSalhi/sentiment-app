"""Contrat protégé : authentification, rôles, erreurs et compatibilité."""
import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.securite import lire_cles

CLIENT = {"X-API-Key": "test-client-key-123456"}
ADMIN = {"X-API-Key": "test-admin-key-123456"}


@pytest.fixture
def session():
    with TestClient(app) as session:
        yield session


@pytest.mark.parametrize("headers", [{}, {"X-API-Key": "incorrect"}])
def test_cle_refusee(session, headers):
    r = session.post("/v1/predict", headers=headers, json={"text": "Très satisfait"})
    assert r.status_code == 401
    assert r.json()["erreur"]["code"] == "NON_AUTHENTIFIE"
    assert "incorrect" not in r.text


@pytest.mark.parametrize("headers", [CLIENT, ADMIN])
def test_prediction(session, headers):
    r = session.post("/v1/predict", headers=headers, json={"text": "Très satisfait"})
    assert r.status_code == 200
    assert 0 <= r.json()["score"] <= 1


def test_roles(session):
    assert session.get("/v1/modele").status_code == 401
    r = session.get("/v1/modele", headers=CLIENT)
    assert r.status_code == 403
    assert r.json()["erreur"]["code"] == "ACCES_REFUSE"
    r = session.get("/v1/modele", headers=ADMIN)
    assert r.status_code == 200
    assert r.json()["seuil_abstention"] == 0.6
    assert r.json()["metrics"]["f1_macro"] >= 0.85


@pytest.mark.parametrize("payload", [{}, {"text": " "}, {"text": 42}, {"text": "a" * 2001}])
def test_validation(session, payload):
    r = session.post("/v1/predict", headers=CLIENT, json=payload)
    assert r.status_code == 422
    assert r.json()["erreur"]["code"] == "ENTREE_INVALIDE"
    assert r.json()["erreur"]["champs"][0]["champ"] == "body.text"


def test_compatibilite(session):
    r = session.post("/predict", json={"text": "Très satisfait"})
    assert r.status_code == 200
    assert r.headers["deprecation"] == "true"
    assert "/v1/predict" in r.headers["link"]
    assert session.get("/health").status_code == 200
    assert session.get("/v1/health").status_code == 200


def test_cors(session):
    headers = {"Origin": "http://localhost:5500", "Access-Control-Request-Method": "POST",
               "Access-Control-Request-Headers": "Content-Type,X-API-Key"}
    assert session.options("/v1/predict", headers=headers).status_code == 200
    headers["Origin"] = "http://localhost:5600"
    assert session.options("/v1/predict", headers=headers).status_code == 400


@pytest.mark.parametrize("config", ["short:client", "long-enough-key-123:root",
                                  "long-enough-key-123", "long-enough-key-123:client,long-enough-key-123:admin"])
def test_configuration_invalide(config):
    with pytest.raises(ValueError, match="API_KEYS invalide"):
        lire_cles(config)


def test_configuration_valide():
    assert lire_cles("") == {}
    assert lire_cles("long-enough-key-123:admin") == {"long-enough-key-123": "admin"}


def test_modele_indisponible(session):
    session.app.state.model = None
    assert session.get("/v1/health").status_code == 503
    assert session.post("/v1/predict", headers=CLIENT, json={"text": "avis"}).status_code == 503
    assert session.get("/v1/modele", headers=ADMIN).status_code == 503


def test_panne_prediction(session, monkeypatch):
    def fail(text):
        raise RuntimeError("secret")
    monkeypatch.setattr(session.app.state.model, "predict", fail)
    r = session.post("/v1/predict", headers=CLIENT, json={"text": "avis"})
    assert r.status_code == 500
    assert "secret" not in r.text
    assert r.json()["erreur"]["code"] == "ERREUR_INTERNE"


def test_metriques_absentes(session, monkeypatch):
    from pathlib import Path

    def fail(*args, **kwargs):
        raise OSError("inaccessible")
    monkeypatch.setattr(Path, "read_text", fail)
    assert session.get("/v1/modele", headers=ADMIN).status_code == 503


def test_route_absente(session):
    assert session.get("/v1/absente").json()["erreur"]["code"] == "INTROUVABLE"
