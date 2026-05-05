# Reflexion critica

## Fortalezas del enfoque

- **Interpretabilidad**: cada etapa tiene una funcion clara y resultados auditables.
- **Control del flujo**: transiciones condicionales explicitas en lugar de decisiones opacas.
- **Resiliencia**: la relajacion progresiva evita fallos tempranos por restricciones muy estrictas.
- **Escalabilidad conceptual**: permite agregar nuevas actividades (riesgo, colegios, movilidad) sin redisenar todo.

## Riesgos y limitaciones

- **Calidad de datos**: la recomendacion depende fuertemente de la actualidad de oferta y senales externas.
- **Sesgos de score**: ponderaciones mal calibradas pueden favorecer zonas o tipos de inmueble de forma injusta.
- **Heuristicas fijas**: la relajacion actual es deterministica y puede no adaptarse a todos los perfiles.
- **Cobertura de contexto urbano**: el ejemplo usa senales simuladas y no integra fuentes en tiempo real.

## Mejoras futuras

- Aprendizaje de preferencias implicitas a partir de feedback del usuario.
- Integracion con APIs reales de portales inmobiliarios y datos de ciudad.
- Ajuste dinamico de pesos del score por segmento de familia.
- Validacion con metricas offline y evaluacion humana de utilidad percibida.
