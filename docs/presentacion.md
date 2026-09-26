# Guion de presentación (10 min) — IE6 a IE9

## 1. Coherencia y resultados (IE6) — 3 min
- Mostrar consulta: abono fin de semana / error E-204.
- En paralelo: chunk recuperado en `manual_soporte.md`.
- Demostrar que la respuesta repite plazos exactos y cita fuente.

## 2. Diagrama de arquitectura (IE7) — 3 min
- Explicar flujo: UI → Agente → Tools → FAISS/API → LLM.
- Destacar separación índice interno vs externo.

## 3. Fundamentación de decisiones (IE8) — 2 min
- Por qué RAG vs solo LLM (evitar alucinaciones en plazos/comisiones).
- Por qué agente vs pipeline fijo (routing + API mock).
- Parámetros: chunk 350, top-k 3, temperature 0.1.

## 4. Evidencia en vivo (IE9) — 2 min
- Ejecutar `streamlit run src/app.py`.
- Consulta normativa: "¿Puedo pedir tarjeta del cliente?"
- Consulta transacción: TX-20250908-002.
- Mostrar salida de `pytest tests/ -v`.

## Apoyo visual sugerido
- Slide 1: Problema VerifiPay
- Slide 2: Diagrama (`docs/arquitectura.md`)
- Slide 3: Demo + métricas objetivo
- Slide 4: Pruebas y conclusiones
