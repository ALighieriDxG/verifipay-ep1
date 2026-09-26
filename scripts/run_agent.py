"""Punto de entrada CLI para consultas puntuales."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.agent import ask, build_agent_executor


def main() -> None:
    parser = argparse.ArgumentParser(description="Consulta al agente VerifiPay")
    parser.add_argument("question", help="Pregunta del comercio")
    parser.add_argument("--reindex", action="store_true", help="Reconstruye índices FAISS")
    parser.add_argument("--json", action="store_true", help="Salida en JSON")
    args = parser.parse_args()

    executor = build_agent_executor(force_reindex=args.reindex)
    result = ask(executor, args.question)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result.get("output", ""))


if __name__ == "__main__":
    main()
