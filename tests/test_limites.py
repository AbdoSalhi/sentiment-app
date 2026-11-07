"""Frontières du contrat HTTP et propriétés sur les textes Unicode."""

import pytest
from fastapi.testclient import TestClient
from hypothesis import given, settings
from hypothesis import strategies as st

from api.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as session:
        yield session


@pytest.mark.parametrize(
    "payload,status",
    [
        ({"text": ""}, 422),
        ({"text": "   "}, 422),
        ({"text": "a"}, 200),
        ({"text": "a" * 2000}, 200),
        ({"text": "a" * 2001}, 422),
        ({}, 422),
        ({"text": 42}, 422),
        ({"text": None}, 422),
    ],
)
def test_frontieres(client, payload, status):
    response = client.post("/predict", json=payload)
    assert response.status_code == status
    if status == 422:
        errors = response.json()["detail"]
        assert isinstance(errors, list) and errors
        assert errors[0]["loc"] == ["body", "text"]
        assert errors[0]["type"] and errors[0]["msg"]


def test_corps_non_json(client):
    response = client.post("/predict", content="ceci n'est pas du JSON", headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert isinstance(errors, list)
    assert errors[0]["type"] == "json_invalid"
    assert errors[0]["loc"][0] == "body"


@settings(max_examples=50, deadline=None)
@given(texte=st.text(min_size=1, max_size=2000).filter(lambda texte: bool(texte.strip())))
def test_tout_texte_non_blanc(client, texte):
    response = client.post("/predict", json={"text": texte})
    assert response.status_code == 200
    result = response.json()
    assert result["label"] in {"POSITIVE", "NEGATIVE", "INDETERMINE"}
    assert 0 <= result["score"] <= 1
    assert result["text"] == texte


@settings(max_examples=40, deadline=None)
@given(texte=st.text(alphabet=" \t\n\r\v\f\x85\xa0\u2003\u2028\u2029\u3000", min_size=1, max_size=2000))
def test_tout_texte_blanc(client, texte):
    response = client.post("/predict", json={"text": texte})
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)
