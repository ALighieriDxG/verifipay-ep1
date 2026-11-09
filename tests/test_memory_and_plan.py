"""Pruebas de planificación, memoria y rechazo de datos de tarjeta. No usan API."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.agent import messages_to_history
from src.memory_store import MemoryStore, contiene_dato_sensible
from src.planning import planificar, reevaluar


def _nombres(plan: dict) -> list[str]:
    return [paso["herramienta"] for paso in plan["pasos"]]


def test_plan_mixto_prioriza_transaccion_y_cierra_con_ticket():
    plan = planificar(
        "Soy de Ferretería Norte. Necesito el estado de TX-20250908-002 "
        "y cuándo depositan las ventas del fin de semana."
    )
    nombres = _nombres(plan)
    assert nombres.index("consultar_estado_transaccion") < nombres.index("registrar_ticket")
    assert "buscar_documentacion_interna" in nombres
    assert plan["estado_ticket"] == "resuelto"
    assert nombres[-1] == "registrar_ticket"


def test_plan_de_tarjeta_prioriza_norma_y_rechaza():
    plan = planificar("¿Puedo enviarte el número de tarjeta del cliente por este chat?")
    assert _nombres(plan)[0] == "buscar_normativa_externa"
    assert plan["estado_ticket"] == "rechazado"


def test_reevaluar_id_inexistente_escala_y_suelta_la_consulta():
    resultado = "No se encontró la transacción TX-99999999-000."
    plan = reevaluar("Disculpa, el identificador era TX-99999999-000.", resultado)
    assert plan["estado_ticket"] == "escalado"
    assert "consultar_estado_transaccion" not in _nombres(plan)
    assert "escalar_operador" in _nombres(plan)
    assert "Identificador inexistente" in plan["ajuste"]


def test_reevaluar_sin_evidencia_escala():
    plan = reevaluar(
        "¿Cuál es la comisión de un medio que no existe?",
        "No encontré evidencia suficiente en la documentación para responder con confianza.",
    )
    assert plan["estado_ticket"] == "escalado"


def test_memoria_recupera_el_caso_de_ferreteria(tmp_path):
    store = MemoryStore(root=tmp_path / "memoria", embedder="hash")
    store.registrar(
        comercio="Ferretería Norte",
        consulta="Estado de TX-20250908-002 y depósito de fin de semana",
        resumen="Transacción pendiente por débito. El depósito del fin de semana es el martes.",
        estado="resuelto",
        transaction_id="TX-20250908-002",
        fuentes="api_mock, manual_soporte.md",
    )
    store.registrar(
        comercio="Boutique Sur",
        consulta="Estado de TX-20250907-015",
        resumen="Transacción devuelta de crédito.",
        estado="resuelto",
        transaction_id="TX-20250907-015",
        fuentes="api_mock",
    )
    resultado = store.buscar("¿Qué quedó pendiente con la ferretería del débito?")
    assert resultado.index("TX-20250908-002") < resultado.index("TX-20250907-015")
    assert "Ferreter" in resultado
    assert (tmp_path / "memoria" / "faiss").exists()


def test_no_guarda_pan_ni_cvv(tmp_path):
    store = MemoryStore(root=tmp_path / "memoria", embedder="hash")
    respuesta = store.registrar(
        comercio="Café Central",
        consulta="El PAN es 4111111111111111 y el CVV 123",
        resumen="Guardar tarjeta",
        estado="resuelto",
        transaction_id="4111111111111111",
        fuentes="chat",
    )
    assert "Rechazado" in respuesta
    assert contiene_dato_sensible("4111111111111111")
    guardado = store.tickets_path.read_text(encoding="utf-8")
    assert "4111111111111111" not in guardado
    assert "TK-0001" in guardado
    assert "rechazado" in guardado


def test_historial_corto_se_queda_con_la_ventana():
    mensajes = [
        {"role": "user" if i % 2 == 0 else "assistant", "content": str(i)}
        for i in range(10)
    ]
    historial = messages_to_history(mensajes, window=4)
    assert len(historial) == 4
    assert historial[0].content == "6"
    assert historial[-1].content == "9"
    assert messages_to_history([]) == []
