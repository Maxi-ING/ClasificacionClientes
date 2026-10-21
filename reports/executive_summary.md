# Resumen ejecutivo

El 10 % de los clientes con mayor gasto concentra el **60.3% de las ventas brutas**. Conviene probar acciones distintas según la actividad de compra de cada grupo.

Se analizaron **4,335 clientes** y **17,822 pedidos**, con ventas brutas de **£8,279,871.60**. El **63.7%** realizó más de un pedido.

## Perfiles y evidencia

| Segmento | Perfil | Clientes | Ventas brutas | Recompra posterior |
|---|---|---:|---:|---:|
| S01 | Baja frecuencia distante | 2,861 | 17.9% | 35.0% |
| S02 | Recurrentes de alto gasto | 1,474 | 82.1% | 77.7% |

## Decisiones para probar

- **S01:** Probar un incentivo de recompra y medir conversión incremental.
- **S02:** Probar beneficios de fidelización y medir recompra y margen.

## Cómo leer estos resultados

Observación: `2010-09-01` ≤ fecha < `2011-09-01`. Evaluación: `2011-09-01` ≤ fecha < `2011-11-30` (90 días). Se cuenta como recompra al menos un pedido positivo posterior. El denominador incluye todos los clientes del segmento, compren después o no.

KMeans seleccionó **2 grupos**. Silhouette: **0.466**. ARI medio por submuestreo: **0.989**. La selección usa exclusivamente el periodo de observación.

El gasto es bruto, en GBP. Las cancelaciones se informan aparte. Los registros sin ID no forman parte de los segmentos. La tienda incluye mayoristas: un gasto alto no permite inferir por sí solo fidelidad, rentabilidad ni satisfacción.

Las tasas posteriores son descriptivas. No demuestran efectos de las acciones propuestas ni constituyen una predicción individual de abandono.
