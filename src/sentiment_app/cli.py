"""Commande sentiment."""
import argparse
import json
import sys

from sentiment_app import __version__, predict


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Classer un avis en français")
    parser.add_argument("texte", nargs="+")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args(argv)
    try:
        result = predict(" ".join(args.texte))
    except ValueError as exc:
        print(f"erreur : {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False) if args.json else
          f"{result['label']} (confiance {result['score']:.0%})")
    return 0
