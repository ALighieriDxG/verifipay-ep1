"""Recorrido EP2 sin modelo: plan, escritura, ajuste y recuperación de memoria.

Escribe en storage/demo_ep2 y no llama al LLM. Sirve para ensayar el guion
antes de la demo con Streamlit.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.api_mock import consultar_transaccion
from src.config import STORAGE_DIR
from src.memory_store import MemoryStore
from src.planning import formatear_plan, planificar, reevaluar

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def _bloque(titulo: str) -> None:
    print()
    print("=" * 72)
    print(titulo)
    print("=" * 72)


def main() -> None:
    store = MemoryStore(root=STORAGE_DIR / "demo_ep2", embedder="hash")
    store.reset()

    consulta_1 = (
        "Soy de Ferretería Norte. Necesito el estado de TX-20250908-002 "
        "y cuándo depositan las ventas del fin de semana."
    )
    _bloque("1. Plan inicial (consulta + escritura)")
    print(consulta_1)
    print()
    print(formatear_plan(planificar(consulta_1)))

    _bloque("2. Herramienta de consulta: estado de la transacción")
    print(consultar_transaccion("TX-20250908-002"))
    print()
    print(
        "Política interna, ya indexada en la EP1 (manual_soporte.md): "
        "las ventas de viernes, sábado y domingo se depositan el martes siguiente antes de las 14:00."
    )

    _bloque("3. Herramienta de escritura: ticket de largo plazo")
    print(
        store.registrar(
            comercio="Ferretería Norte",
            consulta=consulta_1,
            resumen="TX-20250908-002 pendiente, débito, $48.900 CLP. Depósito de fin de semana: martes antes de las 14:00.",
            estado="resuelto",
            transaction_id="TX-20250908-002",
            fuentes="api_mock, manual_soporte.md",
        )
    )

    consulta_2 = "Disculpa, el identificador era TX-99999999-000."
    resultado_api = consultar_transaccion("TX-99999999-000")
    _bloque("4. La condición cambia: el identificador no existe")
    print(consulta_2)
    print(resultado_api)
    print()
    print(formatear_plan(reevaluar(consulta_2, resultado_api)))
    print()
    print(
        store.registrar(
            comercio="Ferretería Norte",
            consulta=consulta_2,
            resumen="TX-99999999-000 no existe en la API. Se escala a un operador. No se informó un estado.",
            estado="escalado",
            transaction_id="TX-99999999-000",
            fuentes="api_mock",
        )
    )

    consulta_3 = "El PAN del cliente es 4111111111111111 y el CVV 123. ¿Lo guardas?"
    _bloque("5. Escritura rechazada: número de tarjeta")
    print(consulta_3)
    print()
    print(formatear_plan(planificar("¿Puedo enviarte el número de tarjeta del cliente por este chat?")))
    print()
    print(
        store.registrar(
            comercio="Ferretería Norte",
            consulta=consulta_3,
            resumen="Guardar el PAN y el CVV en el ticket.",
            estado="resuelto",
            transaction_id="ninguno",
            fuentes="chat",
        )
    )
    guardado = store.tickets_path.read_text(encoding="utf-8")
    print()
    print("¿El archivo contiene el PAN?", "4111111111111111" in guardado)

    _bloque("6. Memoria de largo plazo: ¿qué quedó pendiente con la ferretería?")
    print(store.buscar("¿Qué quedó pendiente con la ferretería del débito?"))

    _bloque("Listo")
    print(f"Tickets en: {store.tickets_path}")
    print("Esta corrida no usa el modelo. Para el mismo guion con el agente, abre el manual y sigue la sesión.")


if __name__ == "__main__":
    main()
