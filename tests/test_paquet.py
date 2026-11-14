"""Ces tests doivent être lancés hors du dépôt sur le paquet installé."""
import importlib.util
import json
import os
import subprocess
import sys

import pytest

spec = importlib.util.find_spec("sentiment_app")
if not (spec and "site-packages" in (spec.origin or "")) and not os.environ.get("VERIFICATION_LIVRABLE"):
    pytest.skip("paquet non installé : lancer scripts/verifier_livrable.py", allow_module_level=True)


def test_installation():
    import sentiment_app

    assert "site-packages" in sentiment_app.__file__
    assert sentiment_app.__version__ == "1.0.0"


@pytest.mark.parametrize("text,label", [("Service impeccable et livraison en avance", "positive"),
                                       ("Produit cassé à l'arrivée", "negative")])
def test_prediction(text, label):
    from sentiment_app import predict

    r = predict(text)
    assert r["label"] == label
    assert 0 <= r["score"] <= 1


def test_refus():
    from sentiment_app import predict

    with pytest.raises(ValueError):
        predict(" ")


def test_cli():
    from pathlib import Path

    cli = Path(sys.executable).with_name("sentiment.exe" if os.name == "nt" else "sentiment")
    result = subprocess.run([str(cli), "Service impeccable", "--json"],
                            check=True, capture_output=True, text=True)
    assert json.loads(result.stdout)["label"] == "positive"


def test_ressource():
    from importlib.resources import files

    assert files("sentiment_app").joinpath("modele/sentiment.joblib").is_file()
