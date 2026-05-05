# Arquitectura del sistema

## Enfoque general

El sistema se implementa como un **proceso multi-etapa** sobre un grafo de decision con LangGraph. Cada actividad es un nodo funcional con responsabilidades acotadas y salidas trazables, lo que evita el patron de agente unico opaco.

## Componentes

- **Estado compartido (`RecommendationState`)**: concentra entradas, resultados intermedios, historico, relajacion y salida final.
- **Capa de actividades (`src/activities/core.py`)**: interpreta requerimientos, analiza zonas, integra contexto externo, consulta ofertas, filtra y calcula score.
- **Politica de relajacion (`src/relaxation.py`)**: aplica cambios graduales cuando no hay resultados suficientes.
- **Evaluador final (`src/evaluator.py`)**: determina si la solucion es aceptable o si requiere nueva iteracion.
- **Orquestador (`src/graph.py`)**: define nodos, transiciones condicionales y loops.

## Decisiones de diseño

1. **Interpretabilidad**: cada nodo deja rastros en `decision_history`.
2. **Control de incertidumbre**: si no hay soluciones, se activa `diagnose_failure` y luego `relax_constraints`.
3. **Convergencia garantizada**: el proceso tiene `max_iterations` y termina incluso si no alcanza aceptacion.
4. **Trazabilidad**: cada relajacion queda en `relaxation_log` con antes/despues y razon.

## Flujo de datos

1. Criterios iniciales -> normalizacion.
2. Seleccion y evaluacion de zonas.
3. Integracion de senales externas por zona.
4. Busqueda de propiedades por zonas viables.
5. Filtrado por restricciones activas.
6. Scoring de alternativas.
7. Decision: aceptar o iterar con relajacion.
8. Explicacion final de recomendaciones.
