"""Sesión de consola con memoria de corto plazo.

Las consultas se acumulan. 'salir' termina.
Con --guion recorre solo las cuatro consultas de la defensa y llama al modelo.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.agent import ask, build_agent_executor, messages_to_history, resumir_pasos

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

GUION = [
    "Soy de Ferretería Norte. Necesito el estado de TX-20250908-002 y cuándo depositan las ventas del fin de semana.",
    "Disculpa, el identificador era TX-99999999-000.",
    "¿Puedo enviarte el número de tarjeta del cliente por este chat?",
    "¿Qué quedó pendiente con Ferretería Norte?",
]


def _turno(executor, pregunta: str, mensajes: list[dict]) -> None:
    print()
    print("-" * 72)
    print("Comercio:", pregunta)
    result = ask(executor, pregunta, chat_history=messages_to_history(mensajes))
    respuesta = result.get("output", "")
    print()
    print(respuesta)
    pasos = resumir_pasos(result)
    if pasos:
        print()
        print("Herramientas:")
        for paso in pasos:
            print(" ·", paso)
    mensajes.append({"role": "user", "content": pregunta})
    mensajes.append({"role": "assistant", "content": respuesta})


def main() -> None:
    parser = argparse.ArgumentParser(description="Sesión VerifiPay con memoria de corto plazo")
    parser.add_argument("--guion", action="store_true", help="Ejecuta las cuatro consultas de la defensa")
    parser.add_argument("--reindex", action="store_true", help="Reconstruye los índices documentales")
    args = parser.parse_args()

    print("Construyendo agente...")
    executor = build_agent_executor(force_reindex=args.reindex)
    mensajes: list[dict] = []

    if args.guion:
        for pregunta in GUION:
            _turno(executor, pregunta, mensajes)
        return

    print("Sesión abierta. Escribe salir para terminar.")
    print("Guion sugerido:")
    for indice, pregunta in enumerate(GUION, start=1):
        print(f"  {indice}. {pregunta}")
    while True:
        try:
            pregunta = input("\nComercio> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not pregunta:
            continue
        if pregunta.lower() in {"salir", "exit", "quit"}:
            break
        _turno(executor, pregunta, mensajes)


if __name__ == "__main__":
    main()
