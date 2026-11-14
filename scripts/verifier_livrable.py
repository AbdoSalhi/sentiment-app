"""Installer la roue dans un venv temporaire et tester hors des sources."""
import os
import shutil
import subprocess
import sys
import tempfile
import venv
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    report = ROOT / "docs" / "livrable-tp4.txt"
    lines: list[str] = []
    try:
        wheels = list((ROOT / "dist").glob("*.whl"))
        sources = list((ROOT / "dist").glob("*.tar.gz"))
        if len(wheels) != 1 or len(sources) != 1:
            raise RuntimeError("Une roue et une distribution source sont requises dans dist/")
        with zipfile.ZipFile(wheels[0]) as archive:
            if "sentiment_app/modele/sentiment.joblib" not in archive.namelist():
                raise RuntimeError("Modèle absent de la roue")
        lines.append("[OK] roue et distribution source présentes, modèle embarqué")
        with tempfile.TemporaryDirectory(prefix="sentiment-verification-") as directory:
            work = Path(directory)
            venv.create(work / "venv", with_pip=True)
            executable = work / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
            env["VERIFICATION_LIVRABLE"] = "1"
            shutil.copy2(ROOT / "tests" / "test_paquet.py", work / "test_paquet.py")
            for command in [
                [str(executable), "-m", "pip", "install", str(wheels[0]), "pytest>=8"],
                [str(executable), "-m", "pytest", "test_paquet.py", "-q"],
            ]:
                result = subprocess.run(command, cwd=work, env=env, text=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                lines.append(result.stdout)
                if result.returncode:
                    raise RuntimeError(f"Commande échouée, code {result.returncode}")
        lines.append("CONFORME : installation et 6 tests hors du dépôt réussis")
        status = 0
    except (RuntimeError, OSError, zipfile.BadZipFile) as exc:
        lines.append(f"NON CONFORME : {exc}")
        status = 1
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(lines[-1])
    print(f"Rapport : {report}")
    return status


if __name__ == "__main__":
    sys.exit(main())
