"""Clés d'API et rôles, sans exposer les secrets dans les erreurs."""
import secrets
from typing import Annotated, Literal, cast

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader

Role = Literal["client", "admin"]
header = APIKeyHeader(name="X-API-Key", auto_error=False)


def lire_cles(configuration: str) -> dict[str, Role]:
    cles: dict[str, Role] = {}
    for entree in configuration.split(","):
        if not entree.strip():
            continue
        cle, separateur, role = entree.strip().partition(":")
        if not separateur or len(cle) < 16 or role not in {"client", "admin"}:
            raise ValueError("API_KEYS invalide : clé de 16 caractères minimum et rôle client/admin")
        if cle in cles:
            raise ValueError("API_KEYS invalide : clé dupliquée")
        cles[cle] = cast(Role, role)
    return cles


def authentifier(request: Request, cle: str | None = Security(header)) -> Role:
    if cle is None:
        raise HTTPException(401, "Clé d'API manquante : en-tête X-API-Key")
    for connue, role in request.app.state.api_keys.items():
        if secrets.compare_digest(cle.encode(), connue.encode()):
            return cast(Role, role)
    raise HTTPException(401, "Clé d'API refusée")


def administrateur(role: Annotated[Role, Security(authentifier)]) -> Role:
    if role != "admin":
        raise HTTPException(403, "Accès refusé au rôle client")
    return role
