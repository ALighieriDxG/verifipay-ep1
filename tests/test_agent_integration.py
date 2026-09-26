"""Prueba end-to-end del agente (requiere LLM_API_KEY)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.agent import ask, build_agent_executor
from src.config import LLM_API_KEY


pytestmark = pytest.mark.skipif(not LLM_API_KEY, reason="Requiere LLM_API_KEY en .env")


@pytest.fixture(scope="module")
def executor():
    return build_agent_executor(force_reindex=False)


def test_agent_error_e204(executor):
    result = ask(executor, "Mi terminal muestra error E-204, ¿qué debo hacer?")
    answer = result["output"].lower()
    assert "e-204" in answer or "conex" in answer or "wi-fi" in answer


def test_agent_transaction_lookup(executor):
    result = ask(executor, "Consulta el estado de TX-20250908-002")
    answer = result["output"].lower()
    assert "pendiente" in answer or "tx-20250908-002" in answer
