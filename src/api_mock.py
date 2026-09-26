"""API simulada de consulta de transacciones."""

from __future__ import annotations

TRANSACTIONS = {
    "TX-20250908-001": {
        "estado": "abonado",
        "monto": 125000,
        "medio": "crédito",
        "fecha_abono": "2025-09-10",
        "comercio": "Café Central",
    },
    "TX-20250908-002": {
        "estado": "pendiente",
        "monto": 48900,
        "medio": "débito",
        "fecha_abono": "2025-09-09",
        "comercio": "Ferretería Norte",
    },
    "TX-20250907-015": {
        "estado": "devuelto",
        "monto": 32000,
        "medio": "crédito",
        "fecha_abono": "N/A",
        "comercio": "Boutique Sur",
    },
}


def consultar_transaccion(transaction_id: str) -> str:
    """Consulta el estado de una transacción por su identificador."""
    record = TRANSACTIONS.get(transaction_id.strip().upper())
    if not record:
        return (
            f"No se encontró la transacción {transaction_id}. "
            "Verifique el ID en el panel de conciliación."
        )

    return (
        f"Transacción {transaction_id}: estado={record['estado']}, "
        f"monto=${record['monto']:,} CLP, medio={record['medio']}, "
        f"fecha_abono={record['fecha_abono']}, comercio={record['comercio']}."
    )
