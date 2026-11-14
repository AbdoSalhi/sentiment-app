"""Client HTTP : modèle réel en mémoire et pannes réseau simulées."""

import csv
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from api.main import app
from ui import client


@pytest.fixture
def session():
    with TestClient(app, headers={"X-API-Key": "test-client-key-123456"}) as connection:
        yield connection


def test_sante(session):
    result = client.sante(session)
    assert result.ok
    assert result.message == "tfidf-logreg (TP2, models/sentiment.joblib)"


def test_polarites(session):
    for text, label in (
        ("Livraison rapide, produit conforme, très satisfait", "POSITIVE"),
        ("Produit cassé et service injoignable, à fuir", "NEGATIVE"),
    ):
        result = client.predire(session, text)
        assert result.ok and result.label == label
        assert 0.5 <= result.score <= 1


def test_abstention(session):
    result = client.predire(session, "xqzvb wlkptr grombu")
    assert result.ok and result.label == "INDETERMINE"
    assert result.score == 0.5162


def test_refus_422(session):
    for text in ("", "   ", "a" * 2001):
        result = client.predire(session, text)
        assert not result.ok and result.message == client.REFUS


def test_modele_indisponible_503(session):
    del app.state.model
    assert client.sante(session).message == client.SANS_MODELE
    assert client.predire(session, "Avis client").message == client.SANS_MODELE


def test_api_injoignable():
    def offline(request):
        raise httpx.ConnectError("détail réseau interne", request=request)

    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(offline)) as session:
        for result in (client.sante(session), client.predire(session, "Avis client")):
            assert not result.ok and result.message == client.INJOIGNABLE


def test_lot_et_resume(session):
    path = Path(__file__).resolve().parents[1] / "data" / "avis_exemple.csv"
    with path.open(encoding="utf-8", newline="") as stream:
        texts = [row["text"] for row in csv.DictReader(stream)]
    results = client.predire_lot(session, texts)
    assert len(results) == 6 and all(result.ok for result in results)
    assert client.resumer(results) == {"INDETERMINE": 1, "NEGATIVE": 2, "POSITIVE": 3}
    assert [result.label for result in results] == [
        "POSITIVE", "NEGATIVE", "INDETERMINE", "POSITIVE", "NEGATIVE", "POSITIVE",
    ]


def test_lot_avec_refus(session):
    results = client.predire_lot(session, ["   ", "xqzvb wlkptr grombu"])
    assert results[0].message == client.REFUS
    assert results[1].label == "INDETERMINE"
    assert client.resumer(results) == {"INDETERMINE": 1, "ERREUR": 1}
    assert client.predire_lot(session, []) == []
    assert client.resumer([]) == {}


@pytest.mark.parametrize("operation", [client.sante, lambda session: client.predire(session, "Avis")])
def test_timeout(operation):
    def timeout(request):
        raise httpx.ReadTimeout("détail interne", request=request)

    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(timeout)) as session:
        result = operation(session)
        assert not result.ok and result.message == client.DELAI_DEPASSE


@pytest.mark.parametrize("status", [401, 404, 500])
def test_erreur_http_sans_detail_interne(status):
    def response(request):
        return httpx.Response(status, json={"detail": "secret interne"})

    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(response)) as session:
        for result in (client.sante(session), client.predire(session, "Avis")):
            assert not result.ok
            if status == 401:
                assert "API_KEY" in result.message
            else:
                assert str(status) in result.message
            assert "secret" not in result.message


@pytest.mark.parametrize(
    "payload",
    [None, [], {}, {"label": "AUTRE", "score": 0.8}, {"label": [], "score": 0.8},
     {"label": "POSITIVE", "score": True}, {"label": "POSITIVE", "score": "0.9"},
     {"label": "POSITIVE", "score": -1}, {"label": "POSITIVE", "score": 1.1}],
)
def test_prediction_invalide(payload):
    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json=payload),
    )) as session:
        assert client.predire(session, "Avis").message == client.REPONSE_INVALIDE


@pytest.mark.parametrize("payload", [[], {}, {"status": "KO", "model": "test"}, {"status": "OK", "model": 42}])
def test_sante_invalide(payload):
    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json=payload),
    )) as session:
        assert client.sante(session).message == client.REPONSE_INVALIDE


def test_json_invalide():
    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(
        lambda request: httpx.Response(200, text="pas du JSON"),
    )) as session:
        assert client.sante(session).message == client.REPONSE_INVALIDE
        assert client.predire(session, "Avis").message == client.REPONSE_INVALIDE


def test_adresse_configurable(monkeypatch):
    monkeypatch.setenv("API_URL", "http://127.0.0.1:8123")
    with client.creer_session() as session:
        assert str(session.base_url) == "http://127.0.0.1:8123"
