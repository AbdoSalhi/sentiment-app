"""Construire une distribution embarquant le modèle actuel."""
import shutil
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
model = root / "models" / "sentiment.joblib"
if not model.is_file():
    raise SystemExit("Entraîner d'abord : python src/make_demo.py puis python src/train.py")
target = root / "src" / "sentiment_app" / "modele"
target.mkdir(parents=True, exist_ok=True)
shutil.copy2(model, target / model.name)
subprocess.run([sys.executable, "-m", "build"], cwd=root, check=True)
