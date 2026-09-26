"""Pruebas unitarias del corpus y API mock."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.api_mock import consultar_transaccion
from src.ingest import load_external_documents, load_internal_documents


def test_internal_documents_loaded():
    docs = load_internal_documents()
    assert len(docs) >= 8
    sources = {doc.metadata.get("source") for doc in docs}
    assert "manual_soporte.md" in sources
    assert "faq_comercios.json" in sources


def test_external_documents_loaded():
    docs = load_external_documents()
    assert len(docs) == 3
    assert all(doc.metadata.get("tipo") == "externo" for doc in docs)


def test_transaction_api_known_id():
    response = consultar_transaccion("TX-20250908-001")
    assert "abonado" in response
    assert "125,000" in response


def test_transaction_api_unknown_id():
    response = consultar_transaccion("TX-INVALID")
    assert "No se encontró" in response
