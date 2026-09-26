# Prompts optimizados — IE2

## System prompt del agente
Ver `src/prompts.py` → `SYSTEM_PROMPT`

**Decisiones de diseño:**
- Rol acotado (soporte VerifiPay) para reducir respuestas genéricas.
- Reglas explícitas de citación y no alucinación.
- Routing implícito vía descripción de herramientas.

## Herramientas (tool descriptions)

| Herramienta | Cuándo la usa el LLM |
|---|---|
| `buscar_documentacion_interna` | Procedimientos, comisiones, plazos, errores |
| `buscar_normativa_externa` | Datos personales, PCI, CMF |
| `consultar_estado_transaccion` | Estado en tiempo real por ID |

## Ejemplo few-shot implícito (FAQ)
El corpus `faq_comercios.json` aporta pares pregunta-respuesta que mejoran la recuperación semántica para consultas frecuentes.

## Control de contexto
- `temperature=0.1` para respuestas deterministas.
- Top-k=3 chunks por recuperación.
- Umbral de confianza 0.35 → escalamiento humano.
