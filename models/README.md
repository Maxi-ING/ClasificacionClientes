# Modelo generado

El proceso crea dos archivos en esta carpeta:

| Archivo | Contenido |
|---|---|
| `segmentation_pipeline.joblib` | Transformación logarítmica, escalado y KMeans ajustados. |
| `model_metadata.json` | Variables, configuración, versiones, checksum y relación entre etiquetas y segmentos. |

No se versionan los binarios. Se reconstruyen con `python -m customer_segmentation.pipeline`.
La copia de metadatos del análisis publicado está en `reports/run_metadata.json`.

Para asignar clientes con RFM calculado sobre una ventana comparable, usa las columnas
`recency`, `frequency` y `monetary` en ese orden. El resultado de `predict` es `cluster`;
su código legible se obtiene del campo `label_map` de los metadatos.

Los códigos S01, S02, etc. se ordenan por gasto mediano en cada ajuste. No identifican por sí
solos el mismo segmento en versiones distintas. Los clientes sin compras positivas en la
ventana no pueden recibir indicadores RFM mediante este proceso.
