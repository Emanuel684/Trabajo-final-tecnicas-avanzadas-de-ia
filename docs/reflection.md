# Reflexion critica

## Fortalezas

- El grafo hace explicito el flujo de decision y evita un agente unico opaco.
- Los agentes tienen responsabilidades limitadas, por lo que sus salidas son mas faciles de inspeccionar.
- La relajacion progresiva conserva trazabilidad y evita cambiar varias restricciones a la vez.
- El sistema puede ejecutarse sin servicios externos, lo que facilita la demostracion academica.

## Limitaciones

- Los datos de propiedades, zonas y senales externas son simulados.
- El parser heuristico puede no capturar expresiones complejas del usuario.
- Las ponderaciones del score son reglas de negocio iniciales, no parametros aprendidos.
- El uso de LLM queda limitado a la interpretacion de requisitos para mantener control sobre el flujo.

## Mejoras futuras

- Integrar portales inmobiliarios o APIs urbanas reales.
- Incorporar feedback del usuario para ajustar pesos del score.
- Agregar validacion contra sesgos por zona o presupuesto.
- Guardar ejecuciones historicas para comparar decisiones entre iteraciones.
