# Recorrido del proyecto

El orden de lectura permite pasar del problema comercial a la evidencia y después al código.

| Paso | Pregunta | Archivo principal | Evidencia de cierre |
|---|---|---|---|
| 1. Fuente | ¿Los datos sirven para analizar compras repetidas? | `data/README.md` | Fuente, licencia y diccionario. |
| 2. Calidad | ¿Qué registros se conservan y por qué? | `notebooks/01_data_quality.ipynb` | `reports/quality_report.json`. |
| 3. Análisis | ¿Cómo compran los clientes y dónde se concentra el gasto? | `notebooks/02_exploratory_analysis.ipynb` | Ventas mensuales y concentración. |
| 4. Indicadores | ¿Cómo se resume cada historial? | `notebooks/03_rfm_features.ipynb` | Tabla RFM validada. |
| 5. Segmentación | ¿Qué agrupamiento es útil y estable? | `notebooks/04_clustering_evaluation.ipynb` | Comparación de 10 candidatos. |
| 6. Interpretación | ¿Qué caracteriza a cada grupo? | `notebooks/05_segment_profiles.ipynb` | Perfiles y recompra posterior. |
| 7. Presentación | ¿Qué decisiones se pueden probar? | `reports/executive_summary.md` | Recomendaciones y dashboard. |

Todas estas etapas están implementadas en esta versión. El efecto de campañas queda como
trabajo futuro porque requiere un experimento y datos nuevos.

## Responsabilidades del código

Los módulos están dentro de `src/customer_segmentation/`.

| Archivo | Responsabilidad |
|---|---|
| `download.py` | Obtener el original y registrar checksum. |
| `cleaning.py` | Normalizar columnas, resolver copias entre hojas y auditar exclusiones. |
| `analysis.py` | Resumir compras y concentración. |
| `features.py` | Construir RFM y separar periodos. |
| `modeling.py` | Comparar y ajustar los agrupamientos. |
| `profiling.py` | Describir los grupos en unidades de negocio. |
| `evaluation.py` | Medir actividad posterior con un denominador fijo. |
| `plotting.py` | Crear gráficos para informes. |
| `reporting.py` | Redactar el resumen desde los resultados calculados. |
| `pipeline.py` | Coordinar los pasos y guardar sus salidas. |

## Versionado

`dev` reúne commits pequeños por responsabilidad. El pull request a `main` permite revisar
el conjunto antes de integrarlo. Las verificaciones de GitHub comprueban calidad del código,
cálculos conocidos, proceso integrado y navegación del dashboard sin descargar el XLSX.
