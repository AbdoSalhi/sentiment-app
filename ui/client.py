"""Appels HTTP et messages prêts à afficher, sans accès au modèle."""

import math
import os
from collections import Counter
from dataclasses import dataclass

import httpx
from dotenv import load_dotenv

load_dotenv()

VERDICTS = {
    "POSITIVE": "Avis positif",
    "NEGATIVE": "Avis négatif",
    "INDETERMINE": "Je ne sais pas : à faire vérifier par un humain",
}
REFUS = "Texte refusé : vide, fait d'espaces, ou de plus de 2000 caractères."
SANS_MODELE = "Modèle non chargé : le service est temporairement indisponible."
INJOIGNABLE = "API injoignable : lancez d'abord uvicorn api.main:app."
DELAI_DEPASSE = "L'API met trop de temps à répondre. Réessayez dans un instant."
REPONSE_INVALIDE = "Réponse de l'API invalide. Réessayez ou contactez le responsable du service."


@dataclass(frozen=True)
class Reponse:
    ok: bool
    label: str | None = None
    score: float | None = None
    message: str = ""


def creer_session() -> httpx.Client:
    return httpx.Client(base_url=os.environ.get("API_URL", "http://127.0.0.1:8000"), timeout=10,
                        headers={"X-API-Key": os.environ.get("API_KEY", "")})


def _erreur_http(response: httpx.Response) -> Reponse | None:
    if response.status_code == 200:
        return None
    try:
        code = response.json().get("erreur", {}).get("code", "")
    except (ValueError, AttributeError):
        code = ""
    if code == "NON_AUTHENTIFIE" or response.status_code == 401:
        return Reponse(False, message="Clé d'API absente ou refusée : configurez API_KEY.")
    if code == "ACCES_REFUSE" or response.status_code == 403:
        return Reponse(False, message="Accès refusé pour cette clé d'API.")
    if code == "ENTREE_INVALIDE" or response.status_code == 422:
        return Reponse(False, message=REFUS)
    if response.status_code == 503:
        return Reponse(False, message=SANS_MODELE)
    return Reponse(False, message=f"Erreur interne de l'API (code {response.status_code}).")


def sante(session: httpx.Client) -> Reponse:
    try:
        response = session.get("/v1/health")
        error = _erreur_http(response)
        if error is not None:
            return error
        data = response.json()
        if not isinstance(data, dict) or data.get("status") != "OK":
            return Reponse(False, message=REPONSE_INVALIDE)
        model = data.get("model")
        if not isinstance(model, str) or not model:
            return Reponse(False, message=REPONSE_INVALIDE)
        return Reponse(True, message=model)
    except httpx.TimeoutException:
        return Reponse(False, message=DELAI_DEPASSE)
    except httpx.RequestError:
        return Reponse(False, message=INJOIGNABLE)
    except ValueError:
        return Reponse(False, message=REPONSE_INVALIDE)


def predire(session: httpx.Client, texte: str) -> Reponse:
    try:
        response = session.post("/v1/predict", json={"text": texte})
        error = _erreur_http(response)
        if error is not None:
            return error
        data = response.json()
        if not isinstance(data, dict):
            return Reponse(False, message=REPONSE_INVALIDE)
        label, score = data.get("label"), data.get("score")
        if (
            not isinstance(label, str) or label not in VERDICTS
            or isinstance(score, bool) or not isinstance(score, (int, float))
            or not math.isfinite(score) or not 0 <= score <= 1
        ):
            return Reponse(False, message=REPONSE_INVALIDE)
        return Reponse(True, label=label, score=float(score))
    except httpx.TimeoutException:
        return Reponse(False, message=DELAI_DEPASSE)
    except httpx.RequestError:
        return Reponse(False, message=INJOIGNABLE)
    except ValueError:
        return Reponse(False, message=REPONSE_INVALIDE)


def predire_lot(session: httpx.Client, textes: list[str]) -> list[Reponse]:
    return [predire(session, texte) for texte in textes]


def resumer(reponses: list[Reponse]) -> dict[str, int]:
    counts = Counter(r.label if r.ok and r.label in VERDICTS else "ERREUR" for r in reponses)
    return {label: counts[label] for label in (*sorted(VERDICTS), "ERREUR") if counts[label]}
