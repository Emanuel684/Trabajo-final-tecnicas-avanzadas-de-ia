# Arquitectura del sistema

## Enfoque

El sistema usa LangGraph como controlador principal. Cada agente participa en una etapa acotada y el grafo decide las transiciones, los reintentos y la terminacion.

## Componentes

- `RecommendationState`: conserva criterios originales, criterios actuales, resultados intermedios, trazas, diagnosticos, relajaciones y recomendaciones.
- `requirements_agent`: convierte texto libre en criterios estructurados. Puede usar LLM si hay `OPENAI_API_KEY`; si no, usa heuristicas.
- `zone_agent`: identifica y evalua zonas candidatas con datos locales.
- `signals_agent`: agrega contexto urbano simulado por zona.
- `property_agent`: consulta ofertas locales, filtra restricciones y calcula scores.
- `evaluation_agent`: valida suficiencia, diagnostica fallos, aplica relajacion progresiva y genera explicaciones.
- `housing_tools`: centraliza operaciones deterministicas para que los agentes sean auditables.

## Trazabilidad

El sistema registra decisiones en `decision_history`, acciones por agente en `agent_traces` y modificaciones de criterios en `relaxation_log`. Esto permite explicar por que se acepto una recomendacion o por que fue necesario relajar condiciones.
