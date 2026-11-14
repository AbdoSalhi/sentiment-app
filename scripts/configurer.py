"""Créer des clés locales sans les afficher ni remplacer une configuration existante."""
import secrets
from pathlib import Path

path = Path(__file__).resolve().parents[1] / ".env"
if path.exists():
    print(".env existe déjà : configuration conservée")
else:
    client, admin = secrets.token_urlsafe(24), secrets.token_urlsafe(24)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(f"API_KEYS={client}:client,{admin}:admin\nAPI_KEY={client}\n"
                     "API_URL=http://127.0.0.1:8000\n"
                     "CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500\n")
    print(".env créé avec deux clés locales distinctes ; conserver ce fichier privé")
