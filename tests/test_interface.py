"""Page Streamlit exécutée par AppTest, API branchée par TestClient."""

import ast
import io
import json
from pathlib import Path

import httpx
import pandas as pd
import pytest
import streamlit as st
from fastapi.testclient import TestClient
from streamlit.testing.v1 import AppTest

from api.main import app
from ui import client

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def page(monkeypatch):
    monkeypatch.setattr(client, "creer_session", lambda: TestClient(app, headers={"X-API-Key": "test-client-key-123456"}))
    return AppTest.from_file(str(ROOT / "ui" / "app.py"), default_timeout=20)


def test_accueil(page):
    page.run()
    assert not page.exception
    assert page.title[0].value == "Analyse de sentiment des avis"
    assert "API prête : tfidf-logreg" in page.caption[0].value
    assert [tab.label for tab in page.tabs] == ["Un avis", "Un fichier d'avis"]


def test_polarites(page):
    for text, label, score in (
        ("Livraison rapide, produit conforme, très satisfait", "Avis positif", "78%"),
        ("Produit cassé et service injoignable, à fuir", "Avis négatif", "75%"),
    ):
        page.run()
        page.text_area[0].input(text)
        page.button[0].click().run()
        assert not page.exception
        assert page.metric[0].label == label
        assert page.metric[0].value == score


def test_abstention(page):
    page.run()
    page.text_area[0].input("xqzvb wlkptr grombu")
    page.button[0].click().run()
    assert not page.exception
    assert page.metric[0].label == client.VERDICTS["INDETERMINE"]
    assert page.metric[0].value == "52%"
    assert "un humain doit trancher" in page.info[0].value


def test_texte_blanc(page):
    page.run()
    page.text_area[0].input("   ")
    page.button[0].click().run()
    assert not page.exception
    assert page.warning[0].value == client.REFUS
    assert not page.metric


def test_api_arretee(page, monkeypatch):
    page.run()
    assert not page.error

    def offline(request):
        raise httpx.ConnectError("connexion refusée", request=request)

    monkeypatch.setattr(client, "creer_session", lambda: httpx.Client(
        base_url="http://test", transport=httpx.MockTransport(offline),
    ))
    page.run()
    assert not page.exception
    assert page.error[0].value == client.INJOIGNABLE


def test_fichier_et_telechargement(page, monkeypatch):
    contents = (ROOT / "data" / "avis_exemple.csv").read_bytes()
    monkeypatch.setattr(st, "file_uploader", lambda *args, **kwargs: io.BytesIO(contents))
    download = st.download_button
    exported = {}

    def capture(*args, **kwargs):
        exported["data"] = args[1]
        exported["filename"] = kwargs["file_name"]
        return download(*args, **kwargs)

    monkeypatch.setattr(st, "download_button", capture)
    page.run()
    assert not page.exception
    table = page.dataframe[0].value
    assert len(table) == 6
    assert list(table.columns) == ["text", "verdict", "confiance"]
    assert json.loads(page.json[0].value) == {"INDETERMINE": 1, "NEGATIVE": 2, "POSITIVE": 3}
    assert len(page.get("download_button")) == 1
    assert len(page.get("arrow_vega_lite_chart")) == 2
    assert exported["filename"] == "resultats.csv"
    assert exported["data"].startswith(b"\xef\xbb\xbf")
    result = pd.read_csv(io.BytesIO(exported["data"]), encoding="utf-8-sig")
    pd.testing.assert_frame_equal(result, table)


@pytest.mark.parametrize(
    "contents,message,kind",
    [(b"review\nBonjour\n", "Colonne text absente", "error"),
     (b"", "Fichier CSV illisible", "error"),
     (b'text\n"guillemet non ferme', "Fichier CSV illisible", "error"),
     (b"text\n\xff\n", "Fichier CSV illisible", "error"),
     (b"text\n", "aucun avis", "warning")],
)
def test_fichier_invalide(page, monkeypatch, contents, message, kind):
    monkeypatch.setattr(st, "file_uploader", lambda *args, **kwargs: io.BytesIO(contents))
    page.run()
    assert not page.exception
    assert message in getattr(page, kind)[0].value
    assert not page.dataframe
    assert not page.get("download_button")


def test_ligne_vide_refusee(page, monkeypatch):
    monkeypatch.setattr(st, "file_uploader", lambda *args, **kwargs: io.BytesIO(
        b'text\n"   "\nxqzvb wlkptr grombu\n',
    ))
    page.run()
    assert not page.exception
    table = page.dataframe[0].value
    assert table.iloc[0]["verdict"] == client.REFUS
    assert pd.isna(table.iloc[0]["confiance"])
    assert json.loads(page.json[0].value) == {"INDETERMINE": 1, "ERREUR": 1}


@pytest.mark.parametrize("status,message", [(503, client.SANS_MODELE), (500, "Erreur interne de l'API")])
def test_panne_affichee(page, monkeypatch, status, message):
    monkeypatch.setattr(client, "creer_session", lambda: httpx.Client(
        base_url="http://test", transport=httpx.MockTransport(
            lambda request: httpx.Response(status, json={"detail": "secret"}),
        ),
    ))
    page.run()
    page.text_area[0].input("Un avis")
    page.button[0].click().run()
    assert not page.exception
    assert all(message in error.value and "secret" not in error.value for error in page.error)
    assert len(page.error) == 2


def test_interface_sans_import_du_modele():
    for filename in ("app.py", "client.py"):
        tree = ast.parse((ROOT / "ui" / filename).read_text(encoding="utf-8"))
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append((node.module or "").split(".")[0])
        assert not {"api", "src", "predict", "joblib", "sklearn"} & set(imports)
