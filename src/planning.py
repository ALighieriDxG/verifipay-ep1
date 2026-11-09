"""Esquema de planificación del agente de soporte VerifiPay.

El plan es explícito y priorizado. El agente lo pide como herramienta y lo
ajusta cuando una consulta de transacción no existe o cuando no hay evidencia.
"""

from __future__ import annotations

import re

TX_RE = re.compile(r"TX-\d{8}-\d{3}", re.IGNORECASE)

_FOLD = str.maketrans("áéíóúüñ", "aeiouun")

_NORMATIVA = (
    "tarjeta",
    "pan",
    "cvv",
    "pci",
    "ley",
    "19.628",
    "19628",
    "dato personal",
    "datos personales",
    "cmf",
)
_OPERATIVA = (
    "deposit",
    "fin de semana",
    "comisi",
    "devol",
    "e-204",
    "error",
    "terminal",
    "abono",
    "link",
    "plazo",
)
_MEMORIA = (
    "pendiente",
    "quedo",
    "anterior",
    "esa transaccion",
    "mismo comercio",
    "la vez pasada",
    "caso anterior",
    "ferreter",
)
_TARJETA = (
    "numero de tarjeta",
    "nro de tarjeta",
    "pan",
    "cvv",
    "pedir la tarjeta",
    "pida la tarjeta",
    "enviarte el numero",
    "enviarte la tarjeta",
)


def _fold(text: str) -> str:
    return text.lower().translate(_FOLD)


def _pide_tarjeta(consulta: str) -> bool:
    q = _fold(consulta)
    return any(term in q for term in _TARJETA)


def detectar_condiciones(consulta: str) -> dict:
    """Señales de la consulta que cambian el orden de las herramientas."""
    q = _fold(consulta)
    return {
        "ids": [match.group(0).upper() for match in TX_RE.finditer(consulta)],
        "normativa": any(term in q for term in _NORMATIVA),
        "operativa": any(term in q for term in _OPERATIVA),
        "memoria": any(term in q for term in _MEMORIA),
        "pide_tarjeta": _pide_tarjeta(consulta),
    }


def _paso(herramienta: str, prioridad: str, motivo: str) -> dict:
    return {"herramienta": herramienta, "prioridad": prioridad, "motivo": motivo}


def planificar(consulta: str) -> dict:
    """Secuencia priorizada para una consulta nueva."""
    flags = detectar_condiciones(consulta)
    pasos: list[dict] = []

    if flags["pide_tarjeta"] or flags["normativa"]:
        pasos.append(
            _paso(
                "buscar_normativa_externa",
                "alta",
                "La consulta toca datos de tarjeta o norma. Se responde con el corpus externo.",
            )
        )
    if flags["ids"]:
        ids = ", ".join(flags["ids"])
        pasos.append(
            _paso(
                "consultar_estado_transaccion",
                "alta",
                f"Hay identificador ({ids}). El estado se consulta en la API y no en el índice.",
            )
        )
    if flags["operativa"] or not pasos:
        pasos.append(
            _paso(
                "buscar_documentacion_interna",
                "alta",
                "Hay un plazo, un error o una política comercial en el corpus interno.",
            )
        )
    if flags["memoria"] or flags["ids"]:
        pasos.append(
            _paso(
                "recuperar_contexto_casos",
                "media",
                "Puede haber un ticket previo del mismo comercio o de la misma transacción.",
            )
        )

    if flags["pide_tarjeta"]:
        estado = "rechazado"
        objetivo = "Rechazar el dato de tarjeta, citar la norma y dejar constancia sin guardar el número."
    else:
        estado = "resuelto"
        objetivo = "Responder con fuente y cerrar un ticket de atención."

    pasos.append(
        _paso(
            "registrar_ticket",
            "baja",
            "La escritura cierra el flujo. No se guarda PAN, CVV ni RUT.",
        )
    )
    return _numerar(
        {
            "objetivo": objetivo,
            "estado_ticket": estado,
            "ajuste": "",
            "pasos": pasos,
            "condiciones": flags,
        }
    )


def reevaluar(consulta: str, resultado_herramienta: str) -> dict:
    """Ajusta el plan cuando la herramienta cambia la condición del caso."""
    plan = planificar(consulta)
    texto = _fold(resultado_herramienta)
    ajustes: list[str] = []

    if "no se encontro" in texto:
        plan["pasos"] = [
            paso
            for paso in plan["pasos"]
            if paso["herramienta"] != "consultar_estado_transaccion"
        ]
        plan["pasos"].insert(
            0,
            _paso(
                "escalar_operador",
                "alta",
                "La API no tiene el identificador. No se informa un estado inventado.",
            ),
        )
        plan["estado_ticket"] = "escalado"
        ajustes.append("Identificador inexistente: se escala y el ticket queda escalado.")

    if "evidencia suficiente" in texto:
        plan["estado_ticket"] = "escalado"
        ajustes.append(
            "La recuperación quedó bajo el umbral. No se completa la respuesta con conocimiento general."
        )

    if _pide_tarjeta(consulta):
        plan["estado_ticket"] = "rechazado"
        ajustes.append("Solicitud de dato de tarjeta: se rechaza y no se almacena PAN ni CVV.")

    plan["ajuste"] = " ".join(ajustes)
    return _numerar(plan)


def formatear_plan(plan: dict) -> str:
    lineas = [f"Objetivo: {plan['objetivo']}", f"Estado del ticket: {plan['estado_ticket']}"]
    if plan.get("ajuste"):
        lineas.append(f"Ajuste: {plan['ajuste']}")
    for paso in plan["pasos"]:
        lineas.append(
            f"{paso['orden']}. [{paso['prioridad']}] {paso['herramienta']} — {paso['motivo']}"
        )
    return "\n".join(lineas)


def _numerar(plan: dict) -> dict:
    for indice, paso in enumerate(plan["pasos"], start=1):
        paso["orden"] = indice
    return plan
