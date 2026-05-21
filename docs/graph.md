# Grafo de decision

```mermaid
flowchart TD
    startNode["Inicio"] --> parseRequirements["Agente: interpretar requisitos"]
    parseRequirements --> zoneSearch["Agente: identificar zonas"]
    zoneSearch --> zoneEvaluation["Evaluar zonas"]
    zoneEvaluation --> signalAgent["Agente: incorporar señales externas"]
    signalAgent --> propertyAgent["Agente: buscar propiedades"]
    propertyAgent --> filterNode["Filtrar restricciones"]
    filterNode --> scoreNode["Puntuar alternativas"]
    scoreNode --> sufficiencyCheck["Validar suficiencia"]
    sufficiencyCheck -->|"suficiente"| finalEvaluator["Agente evaluador final"]
    sufficiencyCheck -->|"insuficiente"| failureDiagnosis["Diagnosticar fallo"]
    failureDiagnosis --> relaxNode["Relajar una restriccion"]
    relaxNode -->|"hay iteraciones"| zoneSearch
    relaxNode -->|"limite alcanzado"| finalEvaluator
    finalEvaluator -->|"aprobado o rechazado"| explainNode["Explicar salida"]
    finalEvaluator -->|"reintentar"| relaxNode
    explainNode --> endNode["Fin"]
```

## Transiciones

- `check_sufficiency` envia a evaluacion final si hay suficientes alternativas o si ya se alcanzo el limite de iteraciones.
- `diagnose_failure` explica por que no hay resultados adecuados antes de relajar criterios.
- `relax_constraints` modifica una sola variable por iteracion.
- `final_evaluator` aprueba, rechaza o solicita otra relajacion.
