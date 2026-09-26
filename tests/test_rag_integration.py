"""Pruebas de integración RAG (requieren LLM_API_KEY)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import LLM_API_KEY
from src.ingest import ensure_indexes
from src.rag import retrieve_with_scores


pytestmark = pytest.mark.skipif(not LLM_API_KEY, reason="Requiere LLM_API_KEY en .env")


def test_internal_retrieval_weekend_payout():
    internal, _ = ensure_indexes(force=False)
    result = retrieve_with_scores(internal, "¿Cuándo abonan ventas del fin de semana?")
    assert result.chunks
    joined = " ".join(result.chunks).lower()
    assert "martes" in joined or "fin de semana" in joined


def test_external_retrieval_data_protection():
    _, external = ensure_indexes(force=False)
    result = retrieve_with_scores(external, "¿Puedo pedir número de tarjeta al cliente?")
    assert result.chunks
    joined = " ".join(result.chunks).lower()
    assert "tarjeta" in joined or "datos personales" in joined
