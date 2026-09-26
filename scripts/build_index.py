"""Construye los índices vectoriales internos y externos."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.ingest import ensure_indexes


def main() -> None:
    print("Construyendo índices FAISS...")
    internal, external = ensure_indexes(force=True)
    print(f"✓ Índice interno: {internal.index.ntotal} vectores")
    print(f"✓ Índice externo: {external.index.ntotal} vectores")


if __name__ == "__main__":
    main()
