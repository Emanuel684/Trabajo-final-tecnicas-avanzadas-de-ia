# Diagrama del grafo propuesto

```mermaid
flowchart TD
    startNode[Start] --> interpretRequirements
    interpretRequirements --> identifyZones
    identifyZones --> evaluateZones
    evaluateZones --> injectExternalSignals
    injectExternalSignals --> searchProperties
    searchProperties --> filterConstraints
    filterConstraints --> scoreAlternatives
    scoreAlternatives --> checkSufficiency

    checkSufficiency -->|"sufficient=true"| finalEvaluator
    checkSufficiency -->|"sufficient=false"| diagnoseFailure

    diagnoseFailure --> relaxConstraints
    relaxConstraints -->|"iterationCount < maxIterations"| identifyZones
    relaxConstraints -->|"iterationCount >= maxIterations"| finalEvaluator

    finalEvaluator -->|"acceptable=true"| explainOutput
    finalEvaluator -->|"acceptable=false and iterationCount < maxIterations"| relaxConstraints
    finalEvaluator -->|"acceptable=false and iterationCount >= maxIterations"| explainOutput

    explainOutput --> endNode[End]
```

## Logica de transiciones

- `check_sufficiency`: valida si existe el minimo de alternativas elegibles.
- `diagnose_failure`: identifica la causa principal cuando no hay suficiencia.
- `relax_constraints`: modifica una sola variable principal por iteracion.
- `final_evaluator`: aprueba o pide otra iteracion segun cantidad y calidad de resultados.
