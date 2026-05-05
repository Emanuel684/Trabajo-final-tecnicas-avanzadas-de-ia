# Sistema Inteligente de Recomendacion de Vivienda

Sistema multi-etapa basado en LangGraph para recomendar opciones de vivienda a partir de criterios de usuario, zonas, senales externas y oferta inmobiliaria.

## Caracteristicas

- Flujo por grafo con decisiones condicionales y ciclos de reintento.
- Estado compartido y evolutivo entre actividades.
- Relajacion progresiva de restricciones con trazabilidad.
- Evaluador final de aceptabilidad antes de la salida.
- Recomendaciones explicadas con score de cumplimiento.

## Estructura

- `src/state.py`: modelo de estado compartido.
- `src/activities/core.py`: actividades funcionales del sistema.
- `src/relaxation.py`: politica de relajacion gradual.
- `src/evaluator.py`: evaluador final.
- `src/graph.py`: construccion del LangGraph.
- `src/data/`: datos de ejemplo.
- `examples/run_example.py`: ejecucion de ejemplo.
- `docs/`: entregables de arquitectura, grafo y reflexion.

## Instalacion

```bash
pip install -r requirements.txt
```

## Ejecucion de ejemplo

```bash
python examples/run_example.py
```

## Salida esperada

El script imprime:

- Criterios originales y criterios finales.
- Nivel de relajacion aplicado y cambios realizados.
- Historial de decisiones/iteraciones.
- Alternativas recomendadas con score y explicacion.
