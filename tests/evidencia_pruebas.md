# Evidencia de pruebas — VerifiPay Bot Soporte

## Comandos ejecutados

```bash
cd BOT_SOPORTE
pip install -r requirements.txt
python -m pytest tests/ -v
python scripts/build_index.py
python scripts/run_agent.py "¿Cuánto tengo para procesar una devolución?"
streamlit run src/app.py
```

## Resultados esperados

| Prueba | Tipo | Qué valida |
|---|---|---|
| `test_internal_documents_loaded` | Unitaria | Carga de corpus interno |
| `test_external_documents_loaded` | Unitaria | Carga de corpus externo |
| `test_transaction_api_*` | Unitaria | API mock de transacciones |
| `test_internal_retrieval_*` | Integración RAG | Recuperación semántica interna |
| `test_external_retrieval_*` | Integración RAG | Recuperación normativa externa |
| `test_agent_error_e204` | E2E | Agente + herramienta interna |
| `test_agent_transaction_lookup` | E2E | Agente + function calling |

## Capturas sugeridas para la presentación

1. Salida de `python -m pytest tests/ -v` con pruebas en verde.
2. Pantalla de Streamlit respondiendo consulta con cita de fuente.
3. Ejemplo donde el agente invoca `consultar_estado_transaccion`.

## Ejemplo de coherencia dato-respuesta (IE6)

**Consulta:** ¿Cuándo me depositan las ventas del fin de semana?

**Fragmento recuperado:** `manual_soporte.md` — "Ventas realizadas viernes, sábado o domingo se depositan el martes siguiente antes de las 14:00 hrs."

**Respuesta del agente:** Informa plazo de depósito el martes antes de 14:00 hrs y cita `manual_soporte.md`.

**Conclusión:** La respuesta se fundamenta directamente en el chunk recuperado, reduciendo alucinaciones.
